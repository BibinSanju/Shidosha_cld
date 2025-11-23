"""
Views for the courses app.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Course, Module, CourseReview
from .serializers import (
    CategorySerializer,
    CourseListSerializer,
    CourseDetailSerializer,
    CourseCreateUpdateSerializer,
    ModuleSerializer,
    CourseReviewSerializer,
)
from .permissions import IsInstructorOrReadOnly


class CategoryViewSet(viewsets.ModelViewSet):
    """API endpoint for course categories."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'


class CourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for courses.
    List, create, retrieve, update, delete courses.
    """
    queryset = Course.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsInstructorOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['difficulty_level', 'category', 'is_free', 'instructor']
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['created_at', 'enrollment_count', 'average_rating', 'title']

    def get_queryset(self):
        queryset = Course.objects.all()

        # Only show published courses to non-staff users
        if not self.request.user.is_staff:
            if self.action == 'list':
                queryset = queryset.filter(is_published=True)

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return CourseListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CourseCreateUpdateSerializer
        return CourseDetailSerializer

    @action(detail=True, methods=['get'])
    def modules(self, request, slug=None):
        """Get all modules for a course."""
        course = self.get_object()
        modules = course.modules.filter(is_published=True).order_by('order')
        serializer = ModuleSerializer(modules, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def reviews(self, request, slug=None):
        """Get all reviews for a course."""
        course = self.get_object()
        reviews = course.reviews.all()
        serializer = CourseReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def enroll(self, request, slug=None):
        """Enroll in a course."""
        from apps.progress.models import Enrollment

        course = self.get_object()
        user = request.user

        # Check if already enrolled
        if Enrollment.objects.filter(student=user, course=course).exists():
            return Response(
                {'detail': 'Already enrolled in this course.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create enrollment
        enrollment = Enrollment.objects.create(
            student=user,
            course=course,
            status='active'
        )

        # Update enrollment count
        course.enrollment_count += 1
        course.save(update_fields=['enrollment_count'])

        return Response({
            'detail': 'Successfully enrolled in course.',
            'enrollment_id': enrollment.id
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def my_courses(self, request):
        """Get courses created by the current instructor."""
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication required.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        courses = Course.objects.filter(instructor=request.user)
        serializer = CourseListSerializer(courses, many=True)
        return Response(serializer.data)


class ModuleViewSet(viewsets.ModelViewSet):
    """API endpoint for course modules."""
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsInstructorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course']

    def get_queryset(self):
        queryset = Module.objects.all()

        # Filter by course if provided
        course_slug = self.request.query_params.get('course_slug')
        if course_slug:
            queryset = queryset.filter(course__slug=course_slug)

        return queryset


class CourseReviewViewSet(viewsets.ModelViewSet):
    """API endpoint for course reviews."""
    queryset = CourseReview.objects.all()
    serializer_class = CourseReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course', 'rating']

    def get_queryset(self):
        queryset = CourseReview.objects.all()

        # Filter by course if provided
        course_id = self.request.query_params.get('course_id')
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)
