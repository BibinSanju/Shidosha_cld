"""
Lesson models for Shidosha Learning Platform.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.courses.models import Module


class Lesson(models.Model):
    """
    Lesson model representing individual learning content.
    Lessons belong to modules and can contain various content types.
    """
    class ContentType(models.TextChoices):
        TEXT = 'TEXT', _('Text/Article')
        VIDEO = 'VIDEO', _('Video')
        INTERACTIVE = 'INTERACTIVE', _('Interactive')
        QUIZ = 'QUIZ', _('Quiz')
        CODE = 'CODE', _('Coding Exercise')
        MIXED = 'MIXED', _('Mixed Content')

    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    title = models.CharField(
        max_length=200,
        help_text=_('Lesson title')
    )
    description = models.TextField(
        blank=True,
        help_text=_('Lesson overview/summary')
    )
    content_type = models.CharField(
        max_length=20,
        choices=ContentType.choices,
        default=ContentType.TEXT
    )
    content_text = models.TextField(
        blank=True,
        help_text=_('Main text content (markdown supported)')
    )
    video_url = models.URLField(
        blank=True,
        help_text=_('URL for video content (YouTube, Vimeo, etc.)')
    )
    video_duration_seconds = models.IntegerField(
        blank=True,
        null=True,
        help_text=_('Video duration in seconds')
    )
    estimated_duration_minutes = models.IntegerField(
        default=10,
        help_text=_('Estimated time to complete lesson (minutes)')
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text=_('Display order within module')
    )
    is_published = models.BooleanField(
        default=True,
        help_text=_('Whether the lesson is visible to students')
    )
    is_preview = models.BooleanField(
        default=False,
        help_text=_('Whether this lesson can be previewed before enrollment')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Lesson')
        verbose_name_plural = _('Lessons')
        ordering = ['module', 'order']
        unique_together = ['module', 'order']
        indexes = [
            models.Index(fields=['module', 'order']),
        ]

    def __str__(self):
        return f"{self.module.course.title} - {self.module.title} - {self.title}"

    @property
    def next_lesson(self):
        """Get the next lesson in sequence."""
        try:
            return Lesson.objects.filter(
                module=self.module,
                order__gt=self.order,
                is_published=True
            ).order_by('order').first()
        except Lesson.DoesNotExist:
            # Try next module
            next_module = Module.objects.filter(
                course=self.module.course,
                order__gt=self.module.order,
                is_published=True
            ).order_by('order').first()

            if next_module:
                return next_module.lessons.filter(is_published=True).order_by('order').first()
            return None

    @property
    def previous_lesson(self):
        """Get the previous lesson in sequence."""
        try:
            return Lesson.objects.filter(
                module=self.module,
                order__lt=self.order,
                is_published=True
            ).order_by('-order').first()
        except Lesson.DoesNotExist:
            # Try previous module
            prev_module = Module.objects.filter(
                course=self.module.course,
                order__lt=self.module.order,
                is_published=True
            ).order_by('-order').first()

            if prev_module:
                return prev_module.lessons.filter(is_published=True).order_by('-order').first()
            return None


class LessonAttachment(models.Model):
    """
    File attachments for lessons (PDFs, code files, datasets, etc.)
    """
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    title = models.CharField(
        max_length=200,
        help_text=_('Attachment title/description')
    )
    file = models.FileField(
        upload_to='lesson_attachments/',
        help_text=_('Uploaded file')
    )
    file_type = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('File type/extension')
    )
    file_size_bytes = models.BigIntegerField(
        blank=True,
        null=True,
        help_text=_('File size in bytes')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Lesson Attachment')
        verbose_name_plural = _('Lesson Attachments')
        ordering = ['lesson', 'created_at']

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"

    def save(self, *args, **kwargs):
        if self.file:
            # Auto-detect file type from file name
            self.file_type = self.file.name.split('.')[-1].upper()
            # Get file size
            self.file_size_bytes = self.file.size
        super().save(*args, **kwargs)


class LessonNote(models.Model):
    """
    Student notes for lessons.
    Students can take notes while learning.
    """
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='student_notes'
    )
    student = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='lesson_notes',
        limit_choices_to={'role': 'STUDENT'}
    )
    note_text = models.TextField(
        help_text=_('Student note content (markdown supported)')
    )
    timestamp_seconds = models.IntegerField(
        blank=True,
        null=True,
        help_text=_('Timestamp in video (for video lessons)')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Lesson Note')
        verbose_name_plural = _('Lesson Notes')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'lesson']),
        ]

    def __str__(self):
        return f"{self.student.username} - {self.lesson.title}"
