"""
Views for the users app.
"""
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from .models import StudentProfile, InstructorProfile
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UpdateProfileSerializer,
    StudentProfileSerializer,
    InstructorProfileSerializer,
)

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    Anyone can register as a new user.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            'user': UserSerializer(user).data,
            'message': 'User registered successfully. Please log in.'
        }, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user management.
    List, retrieve, update user information.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own profile unless they're staff
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'])
    def update_profile(self, request):
        """Update current user profile."""
        serializer = UpdateProfileSerializer(
            instance=request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            'user': UserSerializer(user).data,
            'message': 'Profile updated successfully.'
        })

    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """
        Get dashboard statistics for the current user.
        For students: enrolled courses, progress, points, etc.
        """
        user = request.user

        if user.is_student:
            from apps.progress.models import Enrollment

            enrollments = Enrollment.objects.filter(student=user)

            stats = {
                'total_enrollments': enrollments.count(),
                'active_courses': enrollments.filter(status='active').count(),
                'completed_courses': enrollments.filter(status='completed').count(),
                'total_points': user.student_profile.total_points if hasattr(user, 'student_profile') else 0,
                'level': user.student_profile.level if hasattr(user, 'student_profile') else 1,
            }
        else:
            # For instructors: courses created, students, etc.
            from apps.courses.models import Course

            courses = Course.objects.filter(instructor=user)
            stats = {
                'total_courses': courses.count(),
                'published_courses': courses.filter(is_published=True).count(),
            }

        return Response(stats)


class StudentProfileViewSet(viewsets.ModelViewSet):
    """API endpoint for student profiles."""
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Students can only see their own profile
        if self.request.user.is_staff:
            return StudentProfile.objects.all()
        return StudentProfile.objects.filter(user=self.request.user)


class InstructorProfileViewSet(viewsets.ModelViewSet):
    """API endpoint for instructor profiles."""
    queryset = InstructorProfile.objects.all()
    serializer_class = InstructorProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Instructors can only see their own profile
        if self.request.user.is_staff:
            return InstructorProfile.objects.all()
        return InstructorProfile.objects.filter(user=self.request.user)
