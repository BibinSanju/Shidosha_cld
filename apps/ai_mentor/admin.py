"""
Admin configuration for AI mentor app.
"""
from django.contrib import admin
from .models import MentorSession, MentorMessage, MentorFeedback


class MentorMessageInline(admin.TabularInline):
    """Inline admin for mentor messages."""
    model = MentorMessage
    extra = 0
    readonly_fields = ['role', 'content', 'model_used', 'tokens_used', 'created_at']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(MentorSession)
class MentorSessionAdmin(admin.ModelAdmin):
    """Admin for mentor sessions."""
    list_display = [
        'student', 'title', 'course', 'lesson',
        'is_active', 'created_at', 'updated_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['student__username', 'title', 'course__title']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [MentorMessageInline]


@admin.register(MentorMessage)
class MentorMessageAdmin(admin.ModelAdmin):
    """Admin for mentor messages."""
    list_display = [
        'session', 'role', 'content_preview', 'model_used',
        'tokens_used', 'created_at'
    ]
    list_filter = ['role', 'model_used', 'created_at']
    search_fields = ['session__student__username', 'content']
    readonly_fields = ['created_at']

    def content_preview(self, obj):
        return obj.content[:100] + ('...' if len(obj.content) > 100 else '')

    content_preview.short_description = 'Content Preview'


@admin.register(MentorFeedback)
class MentorFeedbackAdmin(admin.ModelAdmin):
    """Admin for mentor feedback."""
    list_display = [
        'student', 'message', 'rating', 'was_helpful', 'created_at'
    ]
    list_filter = ['rating', 'was_helpful', 'created_at']
    search_fields = ['student__username', 'comment']
    readonly_fields = ['created_at']
