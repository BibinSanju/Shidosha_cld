"""
Admin configuration for users app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, StudentProfile, InstructorProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User model."""

    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone', 'bio', 'avatar', 'date_of_birth')}),
        (_('Permissions'), {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    """Admin for student profiles."""

    list_display = ['user', 'institution', 'year_of_study', 'branch', 'total_points', 'level']
    list_filter = ['year_of_study', 'preferred_learning_style', 'level']
    search_fields = ['user__username', 'user__email', 'institution', 'branch']
    readonly_fields = ['total_points', 'level', 'created_at', 'updated_at']

    fieldsets = (
        (_('User'), {'fields': ('user',)}),
        (_('Academic Info'), {'fields': ('institution', 'year_of_study', 'branch')}),
        (_('Learning Preferences'), {'fields': ('interests', 'learning_goals', 'preferred_learning_style')}),
        (_('Gamification'), {'fields': ('total_points', 'level')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(InstructorProfile)
class InstructorProfileAdmin(admin.ModelAdmin):
    """Admin for instructor profiles."""

    list_display = ['user', 'title', 'organization', 'verified']
    list_filter = ['verified', 'created_at']
    search_fields = ['user__username', 'user__email', 'organization', 'title']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (_('User'), {'fields': ('user',)}),
        (_('Professional Info'), {'fields': ('title', 'organization', 'expertise')}),
        (_('Links'), {'fields': ('website', 'linkedin')}),
        (_('Verification'), {'fields': ('verified',)}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )
