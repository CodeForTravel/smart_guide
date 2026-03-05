from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from apps.chat.models import ChatThread, ConversationMessage


@database_sync_to_async
def get_thread(thread_id, user):
    try:
        return ChatThread.objects.get(id=thread_id, user=user)
    except ChatThread.DoesNotExist:
        return None


@database_sync_to_async
def save_message(thread, role, text, is_location_triggered=False):
    return ConversationMessage.objects.create(
        thread=thread,
        role=role,
        message_text=text,
        is_location_triggered=is_location_triggered,
    )


class ChatConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for bidirectional text/voice chat and location-triggered narrations.

    Connect: ws/chat/threads/<thread_id>/?token=<jwt>

    Receives from client:
        { "type": "user_message", "text": "..." }

    Sends to client:
        { "type": "ai_reply", "text": "...", "audio_url": null }
        { "type": "poi_narration", "poi_name": "...", "text": "...", "audio_url": null }

    Receives from channel layer (LocationConsumer → ChatConsumer):
        { "type": "poi_narration_trigger", "poi_id": int, "poi_name": str,
          "poi_description": str, "distance_meters": float }
    """

    async def connect(self):
        user = self.scope["user"]
        if not user or not user.is_authenticated:
            await self.close(code=4001)
            return

        thread_id = self.scope["url_route"]["kwargs"]["thread_id"]
        self.thread = await get_thread(thread_id, user)
        if not self.thread:
            await self.close(code=4003)
            return

        # Use chat thread id as the group name so it's independent of tour session
        self.chat_group_name = f"chat_thread_{thread_id}"

        await self.channel_layer.group_add(self.chat_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "chat_group_name"):
            await self.channel_layer.group_discard(self.chat_group_name, self.channel_name)

    async def receive_json(self, content):
        msg_type = content.get("type")

        if msg_type == "user_message":
            text = content.get("text", "").strip()
            if not text:
                return

            await save_message(self.thread, ConversationMessage.RoleChoices.USER, text)

            # TODO: Replace stub with real AI call (e.g. OpenAI)
            ai_text = f"[AI stub] You said: {text}"
            await save_message(self.thread, ConversationMessage.RoleChoices.AI, ai_text)

            await self.send_json(
                {
                    "type": "ai_reply",
                    "text": ai_text,
                    "audio_url": None,  # TODO: TTS integration
                }
            )

    # --- Channel layer event handlers (called by group_send) ---

    async def poi_narration_trigger(self, event):
        """
        Receives a POI trigger from LocationConsumer via the channel layer
        and sends a narration to the connected mobile client.
        """
        poi_name = event["poi_name"]
        description = event["poi_description"]

        # Save location-triggered AI message
        narration_text = description if description else f"You are approaching {poi_name}."
        await save_message(self.thread, ConversationMessage.RoleChoices.AI, narration_text, is_location_triggered=True)

        await self.send_json(
            {
                "type": "poi_narration",
                "poi_name": poi_name,
                "text": narration_text,
                "audio_url": None,  # TODO: TTS integration
            }
        )
