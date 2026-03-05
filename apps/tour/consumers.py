import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone

from apps.tour.services import TourSessionService, POIService


class LocationConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for real-time GPS location tracking during a TourSession.

    Connect: ws/tour/sessions/<session_id>/location/?token=<jwt>
    Receive: { "latitude": float, "longitude": float, "timestamp": "ISO string" }
    Send:    { "type": "location_saved", "path_point_id": int }
             { "type": "poi_triggered", "poi_id": int, "poi_name": str, "distance_meters": float }
    """

    async def connect(self):
        user = self.scope["user"]
        if not user or not user.is_authenticated:
            await self.close(code=4001)
            return

        session_id = self.scope["url_route"]["kwargs"]["session_id"]

        tour_service = TourSessionService()
        self.session = await database_sync_to_async(tour_service.get_active_session_for_user)(session_id, user)
        if not self.session:
            await self.close(code=4003)
            return

        # We no longer hardcode a chat_group_name in connect, because we only push
        # if the session has a linked thread. We will resolve it in receive_json.

        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive_json(self, content):
        latitude = content.get("latitude")
        longitude = content.get("longitude")
        # 1. Take timestamp as timezone.now() rather than input
        timestamp = timezone.now()

        if latitude is None or longitude is None:
            # Silently drop or log error, but 2. Do not send anything as response
            return

        # Save path point by delegating to service
        tour_service = TourSessionService()
        await database_sync_to_async(tour_service.save_path_point)(self.session, latitude, longitude, timestamp)

        # Let the service evaluate location and generate AI narrations
        poi_service = POIService()
        narrations = await database_sync_to_async(poi_service.process_location_for_pois)(
            session=self.session, user=self.scope["user"], latitude=latitude, longitude=longitude
        )

        # Dispatch generated narrations to the ChatConsumer directly (if linked)
        # Check if this tour session is linked to a chat thread.
        chat_thread_id = await database_sync_to_async(
            lambda: (
                getattr(self.session, "chat_thread").id
                if hasattr(self.session, "chat_thread") and self.session.chat_thread
                else None
            )
        )()

        if chat_thread_id and narrations:
            chat_group_name = f"chat_thread_{chat_thread_id}"

            for item in narrations:
                await self.channel_layer.group_send(
                    chat_group_name,
                    {
                        "type": "poi_narration_trigger",
                        "poi_id": item["poi_id"],
                        "poi_name": item["poi_name"],
                        "poi_description": item["narration"],
                        "distance_meters": item["distance_meters"],
                    },
                )
