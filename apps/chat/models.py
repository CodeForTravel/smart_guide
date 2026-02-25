from django.db import models
from common.base_model import BaseModel
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatThread(BaseModel):
    """
    A standalone chat session with the AI. Can be created before a tour starts
    (e.g., for planning) and later linked to a TourSession when the user starts walking.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_threads")
    title = models.CharField(max_length=200, blank=True, help_text="Auto-generated title based on first message")

    # We use a string reference 'tour.TourSession' to avoid circular imports
    # since tour app models likely need to import from chat eventually.
    tour_session = models.OneToOneField(
        "tour.TourSession",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chat_thread",
        help_text="Links this chat history to an active walking tour",
    )

    def __str__(self):
        return f"Chat {self.id} for {self.user.email} - {self.title or 'Untitled'}"


class ConversationMessage(BaseModel):
    """
    Individual messages within a ChatThread. Includes both the automatic
    location-based geography narrations and conversational Q&A from the user.
    """

    class RoleChoices(models.TextChoices):
        USER = "user", "User"
        AI = "ai", "AI"

    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=10, choices=RoleChoices.choices)
    message_text = models.TextField()
    audio_url = models.URLField(max_length=500, blank=True, null=True, help_text="S3/Blob URL to generated TTS audio")
    is_location_triggered = models.BooleanField(
        default=False,
        help_text="True if this was a system-generated narration based on location, False if it was a user Q&A response",
    )

    def __str__(self):
        return f"[{self.created_at}] {self.role.upper()}: {self.message_text[:50]}..."
