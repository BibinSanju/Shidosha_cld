"""
Admin configuration for assessments app.
"""
from django.contrib import admin
from .models import Quiz, Question, Answer, QuizAttempt, QuestionResponse


class AnswerInline(admin.TabularInline):
    """Inline admin for answers."""
    model = Answer
    extra = 4
    fields = ['answer_text', 'is_correct', 'order']


class QuestionInline(admin.StackedInline):
    """Inline admin for questions."""
    model = Question
    extra = 1
    fields = ['question_type', 'question_text', 'explanation', 'points', 'order']
    show_change_link = True


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """Admin for quizzes."""
    list_display = [
        'title', 'course', 'module', 'lesson', 'total_questions',
        'passing_score_percentage', 'is_published', 'created_at'
    ]
    list_filter = ['is_published', 'course', 'created_at']
    search_fields = ['title', 'description', 'course__title']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [QuestionInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'course', 'module', 'lesson')
        }),
        ('Quiz Settings', {
            'fields': (
                'time_limit_minutes', 'passing_score_percentage',
                'max_attempts', 'shuffle_questions', 'shuffle_answers'
            )
        }),
        ('Publishing', {
            'fields': ('is_published',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin for questions."""
    list_display = [
        'quiz', 'question_type', 'question_preview', 'points', 'order'
    ]
    list_filter = ['question_type', 'quiz']
    search_fields = ['question_text', 'quiz__title']
    inlines = [AnswerInline]

    def question_preview(self, obj):
        return obj.question_text[:100] + ('...' if len(obj.question_text) > 100 else '')

    question_preview.short_description = 'Question'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """Admin for answers."""
    list_display = ['question', 'answer_preview', 'is_correct', 'order']
    list_filter = ['is_correct', 'question__quiz']
    search_fields = ['answer_text', 'question__question_text']

    def answer_preview(self, obj):
        return obj.answer_text[:100] + ('...' if len(obj.answer_text) > 100 else '')

    answer_preview.short_description = 'Answer'


class QuestionResponseInline(admin.TabularInline):
    """Inline admin for question responses."""
    model = QuestionResponse
    extra = 0
    readonly_fields = ['question', 'selected_answer', 'text_answer', 'is_correct', 'points_earned']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    """Admin for quiz attempts."""
    list_display = [
        'student', 'quiz', 'status', 'score', 'passed',
        'started_at', 'completed_at'
    ]
    list_filter = ['status', 'passed', 'started_at']
    search_fields = ['student__username', 'quiz__title']
    readonly_fields = [
        'score', 'points_earned', 'points_possible', 'passed',
        'started_at', 'completed_at', 'time_taken_seconds'
    ]
    inlines = [QuestionResponseInline]

    actions = ['recalculate_scores']

    def recalculate_scores(self, request, queryset):
        """Admin action to recalculate scores for selected attempts."""
        for attempt in queryset:
            attempt.calculate_score()
        self.message_user(request, f"Recalculated scores for {queryset.count()} attempts.")

    recalculate_scores.short_description = "Recalculate scores"


@admin.register(QuestionResponse)
class QuestionResponseAdmin(admin.ModelAdmin):
    """Admin for question responses."""
    list_display = [
        'attempt', 'question', 'is_correct', 'points_earned', 'created_at'
    ]
    list_filter = ['is_correct', 'created_at']
    search_fields = ['attempt__student__username', 'question__question_text']
    readonly_fields = ['created_at', 'updated_at']
