"""
Serializers for the progress app.
"""
from rest_framework import serializers
from .models import Enrollment, LessonProgress, LearningStreak


class LessonProgressSerializer(serializers.ModelSerializer):
    """Serializer for lesson progress."""
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = LessonProgress
        fields = [
            'id', 'lesson', 'lesson_title', 'is_completed',
            'completion_percentage', 'time_spent_seconds',
            'last_position_seconds', 'started_at', 'completed_at',
            'last_accessed_at'
        ]
        read_only_fields = ['id', 'started_at', 'completed_at', 'last_accessed_at']


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for course enrollments."""
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_slug = serializers.CharField(source='course.slug', read_only=True)
    current_lesson_id = serializers.SerializerMethodField()
    current_lesson_title = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = [
            'id', 'course', 'course_title', 'course_slug', 'status',
            'progress_percentage', 'enrolled_at', 'completed_at',
            'last_accessed_at', 'current_lesson_id', 'current_lesson_title'
        ]
        read_only_fields = [
            'id', 'progress_percentage', 'enrolled_at',
            'completed_at', 'last_accessed_at'
        ]

    def get_current_lesson_id(self, obj):
        current_lesson = obj.current_lesson
        return current_lesson.id if current_lesson else None

    def get_current_lesson_title(self, obj):
        current_lesson = obj.current_lesson
        return current_lesson.title if current_lesson else None


class LearningStreakSerializer(serializers.ModelSerializer):
    """Serializer for learning streaks."""

    class Meta:
        model = LearningStreak
        fields = [
            'id', 'current_streak_days', 'longest_streak_days',
            'last_activity_date', 'total_learning_days',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'current_streak_days', 'longest_streak_days',
            'last_activity_date', 'total_learning_days',
            'created_at', 'updated_at'
        ]
