from rest_framework import viewsets, permissions
from apps.chat.models import ChatThread
from apps.chat.api.v1.serializers import ChatThreadSerializer


class ChatThreadViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and creating ChatThreads independently of TourSession.
    Users can only view and manage their own chat threads.
    """

    serializer_class = ChatThreadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Prevent swagger generation from throwing an exception with AnonymousUser
        if getattr(self, "swagger_fake_view", False):
            return ChatThread.objects.none()
        return ChatThread.objects.filter(user=self.request.user).order_by("-created_at")
