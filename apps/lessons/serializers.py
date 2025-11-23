"""
Serializers for the lessons app.
"""
from rest_framework import serializers
from .models import Lesson, LessonAttachment, LessonNote


class LessonAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for lesson attachments."""
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = LessonAttachment
        fields = [
            'id', 'title', 'file', 'file_url', 'file_type',
            'file_size_bytes', 'created_at'
        ]
        read_only_fields = ['id', 'file_type', 'file_size_bytes', 'created_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class LessonListSerializer(serializers.ModelSerializer):
    """Serializer for lesson list view (minimal data)."""
    module_title = serializers.CharField(source='module.title', read_only=True)

    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'description', 'module', 'module_title',
            'content_type', 'order', 'estimated_duration_minutes',
            'is_preview', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class LessonDetailSerializer(serializers.ModelSerializer):
    """Serializer for lesson detail view (full data)."""
    module_title = serializers.CharField(source='module.title', read_only=True)
    course_title = serializers.CharField(source='module.course.title', read_only=True)
    course_slug = serializers.CharField(source='module.course.slug', read_only=True)
    attachments = LessonAttachmentSerializer(many=True, read_only=True)
    next_lesson_id = serializers.SerializerMethodField()
    previous_lesson_id = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            'id', 'module', 'module_title', 'course_title', 'course_slug',
            'title', 'description', 'content_type', 'content_text',
            'video_url', 'video_duration_seconds', 'estimated_duration_minutes',
            'order', 'is_published', 'is_preview', 'attachments',
            'next_lesson_id', 'previous_lesson_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_next_lesson_id(self, obj):
        next_lesson = obj.next_lesson
        return next_lesson.id if next_lesson else None

    def get_previous_lesson_id(self, obj):
        prev_lesson = obj.previous_lesson
        return prev_lesson.id if prev_lesson else None


class LessonNoteSerializer(serializers.ModelSerializer):
    """Serializer for lesson notes."""
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = LessonNote
        fields = [
            'id', 'lesson', 'lesson_title', 'note_text',
            'timestamp_seconds', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)
