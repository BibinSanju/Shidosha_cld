"""
Serializers for the AI mentor app.
"""
from rest_framework import serializers
from .models import MentorSession, MentorMessage, MentorFeedback


class MentorMessageSerializer(serializers.ModelSerializer):
    """Serializer for mentor messages."""

    class Meta:
        model = MentorMessage
        fields = [
            'id', 'role', 'content', 'suggested_actions',
            'model_used', 'tokens_used', 'created_at'
        ]
        read_only_fields = [
            'id', 'role', 'model_used', 'tokens_used',
            'suggested_actions', 'created_at'
        ]


class MentorSessionSerializer(serializers.ModelSerializer):
    """Serializer for mentor sessions."""
    messages = MentorMessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    course_title = serializers.CharField(source='course.title', read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = MentorSession
        fields = [
            'id', 'title', 'course', 'course_title', 'lesson',
            'lesson_title', 'is_active', 'message_count',
            'messages', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_message_count(self, obj):
        return obj.messages.count()


class AskMentorSerializer(serializers.Serializer):
    """Serializer for asking the mentor a question."""
    message = serializers.CharField(
        required=True,
        help_text="The question or message to send to the AI mentor"
    )
    session_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="ID of existing session (optional, creates new if not provided)"
    )
    course_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Course context ID (optional)"
    )
    lesson_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Lesson context ID (optional)"
    )


class MentorFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for mentor feedback."""

    class Meta:
        model = MentorFeedback
        fields = [
            'id', 'message', 'rating', 'comment', 'was_helpful', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)
