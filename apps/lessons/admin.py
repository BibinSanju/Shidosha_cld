"""
Admin configuration for lessons app.
"""
from django.contrib import admin
from .models import Lesson, LessonAttachment, LessonNote


class LessonAttachmentInline(admin.TabularInline):
    """Inline admin for lesson attachments."""
    model = LessonAttachment
    extra = 1
    readonly_fields = ['file_type', 'file_size_bytes', 'created_at']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Admin for lessons."""
    list_display = [
        'title', 'module', 'content_type', 'order',
        'estimated_duration_minutes', 'is_published', 'is_preview'
    ]
    list_filter = ['content_type', 'is_published', 'is_preview', 'module__course']
    search_fields = ['title', 'description', 'module__title']
    list_editable = ['order', 'is_published']
    inlines = [LessonAttachmentInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('module', 'title', 'description')
        }),
        ('Content', {
            'fields': (
                'content_type', 'content_text', 'video_url', 'video_duration_seconds'
            )
        }),
        ('Settings', {
            'fields': ('order', 'estimated_duration_minutes', 'is_published', 'is_preview')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LessonAttachment)
class LessonAttachmentAdmin(admin.ModelAdmin):
    """Admin for lesson attachments."""
    list_display = ['title', 'lesson', 'file_type', 'file_size_bytes', 'created_at']
    list_filter = ['file_type', 'created_at']
    search_fields = ['title', 'lesson__title']
    readonly_fields = ['file_type', 'file_size_bytes', 'created_at']


@admin.register(LessonNote)
class LessonNoteAdmin(admin.ModelAdmin):
    """Admin for lesson notes."""
    list_display = ['student', 'lesson', 'timestamp_seconds', 'created_at']
    list_filter = ['created_at']
    search_fields = ['student__username', 'lesson__title', 'note_text']
    readonly_fields = ['created_at', 'updated_at']
