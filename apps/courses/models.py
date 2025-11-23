"""
Course models for Shidosha Learning Platform.
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify


class Category(models.Model):
    """Course categories for organizing courses."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('Icon class or emoji for the category')
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Course(models.Model):
    """
    Course model representing a complete learning course.
    Can contain multiple modules/lessons.
    """
    class DifficultyLevel(models.TextChoices):
        BEGINNER = 'BEGINNER', _('Beginner')
        INTERMEDIATE = 'INTERMEDIATE', _('Intermediate')
        ADVANCED = 'ADVANCED', _('Advanced')
        EXPERT = 'EXPERT', _('Expert')

    title = models.CharField(
        max_length=200,
        help_text=_('Course title')
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        help_text=_('URL-friendly version of title')
    )
    description = models.TextField(
        help_text=_('Detailed course description')
    )
    short_description = models.CharField(
        max_length=500,
        blank=True,
        help_text=_('Brief course overview (for cards/listings)')
    )
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses_created',
        limit_choices_to={'role__in': ['INSTRUCTOR', 'ADMIN']}
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses'
    )
    thumbnail = models.ImageField(
        upload_to='course_thumbnails/',
        blank=True,
        null=True,
        help_text=_('Course thumbnail image')
    )
    difficulty_level = models.CharField(
        max_length=20,
        choices=DifficultyLevel.choices,
        default=DifficultyLevel.BEGINNER
    )
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text=_('List of tags for search and categorization')
    )
    estimated_duration_hours = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=0,
        help_text=_('Estimated time to complete (in hours)')
    )
    prerequisites = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='prerequisite_for',
        help_text=_('Courses that should be completed first')
    )
    is_published = models.BooleanField(
        default=False,
        help_text=_('Whether the course is publicly visible')
    )
    is_free = models.BooleanField(
        default=True,
        help_text=_('Whether the course is free or paid')
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text=_('Course price (if not free)')
    )
    enrollment_count = models.IntegerField(
        default=0,
        help_text=_('Number of enrolled students')
    )
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        help_text=_('Average course rating (0.00 to 5.00)')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_published', '-created_at']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def total_lessons(self):
        """Get total number of lessons across all modules."""
        from apps.lessons.models import Lesson
        return Lesson.objects.filter(module__course=self).count()

    @property
    def total_modules(self):
        """Get total number of modules."""
        return self.modules.count()


class Module(models.Model):
    """
    Module represents a section/chapter within a course.
    Contains ordered lessons.
    """
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='modules'
    )
    title = models.CharField(
        max_length=200,
        help_text=_('Module title')
    )
    description = models.TextField(
        blank=True,
        help_text=_('Module description')
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text=_('Display order within course')
    )
    estimated_duration_hours = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=0,
        help_text=_('Estimated time to complete module (in hours)')
    )
    is_published = models.BooleanField(
        default=True,
        help_text=_('Whether the module is visible to students')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Module')
        verbose_name_plural = _('Modules')
        ordering = ['course', 'order']
        unique_together = ['course', 'order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    @property
    def total_lessons(self):
        """Get total number of lessons in this module."""
        return self.lessons.count()


class CourseReview(models.Model):
    """Student reviews and ratings for courses."""
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='course_reviews',
        limit_choices_to={'role': 'STUDENT'}
    )
    rating = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text=_('Rating from 1 to 5')
    )
    review_text = models.TextField(
        blank=True,
        help_text=_('Written review')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Course Review')
        verbose_name_plural = _('Course Reviews')
        ordering = ['-created_at']
        unique_together = ['course', 'student']

    def __str__(self):
        return f"{self.student.username} - {self.course.title} ({self.rating}/5)"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update course average rating
        self.course.update_average_rating()

    def delete(self, *args, **kwargs):
        course = self.course
        super().delete(*args, **kwargs)
        course.update_average_rating()


# Add method to Course model for updating average rating
def update_average_rating(self):
    """Update the course's average rating based on all reviews."""
    from django.db.models import Avg
    avg_rating = self.reviews.aggregate(Avg('rating'))['rating__avg']
    self.average_rating = avg_rating if avg_rating else 0.00
    self.save(update_fields=['average_rating'])


Course.update_average_rating = update_average_rating
