from rest_framework import serializers

from apps.chat.models import ChatThread, ConversationMessage


class ConversationMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationMessage
        fields = ["id", "role", "message_text", "audio_url", "is_location_triggered", "created_at"]
        read_only_fields = ["id", "role", "audio_url", "is_location_triggered", "created_at"]


class ChatThreadSerializer(serializers.ModelSerializer):
    messages = ConversationMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatThread
        fields = ["id", "title", "tour_session", "messages", "created_at", "updated_at"]
        read_only_fields = ["id", "title", "messages", "created_at", "updated_at"]

    def create(self, validated_data):
        user = self.context["request"].user
        return ChatThread.objects.create(user=user, **validated_data)
