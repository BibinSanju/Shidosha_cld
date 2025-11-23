"""
Serializers for the users app.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, StudentProfile, InstructorProfile


class StudentProfileSerializer(serializers.ModelSerializer):
    """Serializer for student profile."""

    class Meta:
        model = StudentProfile
        fields = [
            'institution', 'year_of_study', 'branch', 'interests',
            'learning_goals', 'preferred_learning_style', 'total_points',
            'level', 'created_at', 'updated_at'
        ]
        read_only_fields = ['total_points', 'level', 'created_at', 'updated_at']


class InstructorProfileSerializer(serializers.ModelSerializer):
    """Serializer for instructor profile."""

    class Meta:
        model = InstructorProfile
        fields = [
            'title', 'organization', 'expertise', 'website',
            'linkedin', 'verified', 'created_at', 'updated_at'
        ]
        read_only_fields = ['verified', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    student_profile = StudentProfileSerializer(read_only=True)
    instructor_profile = InstructorProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'phone', 'bio', 'avatar', 'date_of_birth',
            'student_profile', 'instructor_profile',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'email': {'required': True}
        }


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UpdateProfileSerializer(serializers.Serializer):
    """Serializer for updating user profile based on role."""
    # User fields
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    phone = serializers.CharField(required=False, allow_blank=True)
    bio = serializers.CharField(required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)

    # Student profile fields
    institution = serializers.CharField(required=False, allow_blank=True)
    year_of_study = serializers.IntegerField(required=False, allow_null=True)
    branch = serializers.CharField(required=False, allow_blank=True)
    interests = serializers.ListField(required=False, allow_empty=True)
    learning_goals = serializers.CharField(required=False, allow_blank=True)
    preferred_learning_style = serializers.CharField(required=False, allow_blank=True)

    # Instructor profile fields
    title = serializers.CharField(required=False, allow_blank=True)
    organization = serializers.CharField(required=False, allow_blank=True)
    expertise = serializers.ListField(required=False, allow_empty=True)
    website = serializers.URLField(required=False, allow_blank=True)
    linkedin = serializers.URLField(required=False, allow_blank=True)

    def update(self, instance, validated_data):
        # Update user fields
        user_fields = ['first_name', 'last_name', 'phone', 'bio', 'date_of_birth']
        for field in user_fields:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.save()

        # Update profile based on role
        if instance.is_student and hasattr(instance, 'student_profile'):
            profile = instance.student_profile
            profile_fields = [
                'institution', 'year_of_study', 'branch', 'interests',
                'learning_goals', 'preferred_learning_style'
            ]
            for field in profile_fields:
                if field in validated_data:
                    setattr(profile, field, validated_data[field])
            profile.save()

        elif instance.is_instructor and hasattr(instance, 'instructor_profile'):
            profile = instance.instructor_profile
            profile_fields = ['title', 'organization', 'expertise', 'website', 'linkedin']
            for field in profile_fields:
                if field in validated_data:
                    setattr(profile, field, validated_data[field])
            profile.save()

        return instance
