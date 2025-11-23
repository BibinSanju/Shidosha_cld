"""
Admin configuration for courses app.
"""
from django.contrib import admin
from .models import Category, Course, Module, CourseReview


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin for course categories."""
    list_display = ['name', 'slug', 'parent', 'created_at']
    list_filter = ['parent', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


class ModuleInline(admin.TabularInline):
    """Inline admin for modules within course admin."""
    model = Module
    extra = 1
    fields = ['title', 'order', 'estimated_duration_hours', 'is_published']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin for courses."""
    list_display = [
        'title', 'instructor', 'category', 'difficulty_level',
        'is_published', 'enrollment_count', 'average_rating', 'created_at'
    ]
    list_filter = ['is_published', 'difficulty_level', 'category', 'is_free', 'created_at']
    search_fields = ['title', 'description', 'instructor__username']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['enrollment_count', 'average_rating', 'created_at', 'updated_at']
    filter_horizontal = ['prerequisites']
    inlines = [ModuleInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'instructor', 'category')
        }),
        ('Description', {
            'fields': ('short_description', 'description', 'thumbnail')
        }),
        ('Course Details', {
            'fields': (
                'difficulty_level', 'tags', 'estimated_duration_hours', 'prerequisites'
            )
        }),
        ('Pricing', {
            'fields': ('is_free', 'price')
        }),
        ('Publishing', {
            'fields': ('is_published',)
        }),
        ('Statistics', {
            'fields': ('enrollment_count', 'average_rating'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    """Admin for course modules."""
    list_display = ['title', 'course', 'order', 'is_published', 'created_at']
    list_filter = ['is_published', 'course', 'created_at']
    search_fields = ['title', 'description', 'course__title']
    list_editable = ['order', 'is_published']


@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    """Admin for course reviews."""
    list_display = ['course', 'student', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['course__title', 'student__username', 'review_text']
    readonly_fields = ['created_at', 'updated_at']
