"""
Serializers for the courses app.
"""
from rest_framework import serializers
from .models import Category, Course, Module, CourseReview


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for course categories."""

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'parent', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']


class ModuleSerializer(serializers.ModelSerializer):
    """Serializer for course modules."""
    total_lessons = serializers.ReadOnlyField()

    class Meta:
        model = Module
        fields = [
            'id', 'title', 'description', 'order', 'estimated_duration_hours',
            'is_published', 'total_lessons', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CourseListSerializer(serializers.ModelSerializer):
    """Serializer for course list view (minimal data)."""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'category_name', 'thumbnail', 'difficulty_level', 'tags',
            'estimated_duration_hours', 'is_free', 'price',
            'enrollment_count', 'average_rating', 'created_at'
        ]
        read_only_fields = ['id', 'slug', 'enrollment_count', 'average_rating', 'created_at']


class CourseDetailSerializer(serializers.ModelSerializer):
    """Serializer for course detail view (full data)."""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    instructor_id = serializers.IntegerField(source='instructor.id', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    modules = ModuleSerializer(many=True, read_only=True)
    prerequisites_data = CourseListSerializer(source='prerequisites', many=True, read_only=True)
    total_lessons = serializers.ReadOnlyField()
    total_modules = serializers.ReadOnlyField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'instructor_id', 'instructor_name', 'category', 'category_name',
            'thumbnail', 'difficulty_level', 'tags', 'estimated_duration_hours',
            'prerequisites', 'prerequisites_data', 'is_published', 'is_free',
            'price', 'enrollment_count', 'average_rating', 'modules',
            'total_lessons', 'total_modules', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'slug', 'enrollment_count', 'average_rating',
            'created_at', 'updated_at'
        ]


class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating courses."""

    class Meta:
        model = Course
        fields = [
            'title', 'description', 'short_description', 'category',
            'thumbnail', 'difficulty_level', 'tags', 'estimated_duration_hours',
            'prerequisites', 'is_published', 'is_free', 'price'
        ]

    def create(self, validated_data):
        # Set the instructor to the current user
        validated_data['instructor'] = self.context['request'].user
        return super().create(validated_data)


class CourseReviewSerializer(serializers.ModelSerializer):
    """Serializer for course reviews."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_username = serializers.CharField(source='student.username', read_only=True)

    class Meta:
        model = CourseReview
        fields = [
            'id', 'course', 'student', 'student_name', 'student_username',
            'rating', 'review_text', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'student', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Set the student to the current user
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)
