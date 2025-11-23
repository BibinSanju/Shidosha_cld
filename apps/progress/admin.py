"""
Admin configuration for progress app.
"""
from django.contrib import admin
from .models import Enrollment, LessonProgress, LearningStreak


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """Admin for course enrollments."""
    list_display = [
        'student', 'course', 'status', 'progress_percentage',
        'enrolled_at', 'completed_at'
    ]
    list_filter = ['status', 'enrolled_at', 'completed_at']
    search_fields = ['student__username', 'student__email', 'course__title']
    readonly_fields = ['progress_percentage', 'enrolled_at', 'completed_at', 'last_accessed_at', 'updated_at']

    fieldsets = (
        ('Enrollment Info', {
            'fields': ('student', 'course', 'status')
        }),
        ('Progress', {
            'fields': ('progress_percentage',)
        }),
        ('Timestamps', {
            'fields': ('enrolled_at', 'completed_at', 'last_accessed_at', 'updated_at')
        }),
    )

    actions = ['recalculate_progress']

    def recalculate_progress(self, request, queryset):
        """Admin action to recalculate progress for selected enrollments."""
        for enrollment in queryset:
            enrollment.calculate_progress()
        self.message_user(request, f"Recalculated progress for {queryset.count()} enrollments.")

    recalculate_progress.short_description = "Recalculate progress"


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    """Admin for lesson progress."""
    list_display = [
        'student', 'lesson', 'is_completed', 'completion_percentage',
        'time_spent_seconds', 'last_accessed_at'
    ]
    list_filter = ['is_completed', 'started_at', 'completed_at']
    search_fields = ['student__username', 'lesson__title']
    readonly_fields = ['started_at', 'completed_at', 'last_accessed_at']


@admin.register(LearningStreak)
class LearningStreakAdmin(admin.ModelAdmin):
    """Admin for learning streaks."""
    list_display = [
        'student', 'current_streak_days', 'longest_streak_days',
        'total_learning_days', 'last_activity_date'
    ]
    list_filter = ['last_activity_date']
    search_fields = ['student__username']
    readonly_fields = ['created_at', 'updated_at']
