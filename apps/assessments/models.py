"""
Assessment models for Shidosha Learning Platform.
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.courses.models import Course, Module
from apps.lessons.models import Lesson


class Quiz(models.Model):
    """
    Quiz/test for assessing student knowledge.
    Can be attached to a course, module, or lesson.
    """
    title = models.CharField(
        max_length=200,
        help_text=_('Quiz title')
    )
    description = models.TextField(
        blank=True,
        help_text=_('Quiz description and instructions')
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='quizzes',
        help_text=_('Course this quiz belongs to')
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='quizzes',
        help_text=_('Optional module association')
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='quizzes',
        help_text=_('Optional lesson association')
    )
    time_limit_minutes = models.IntegerField(
        blank=True,
        null=True,
        help_text=_('Time limit in minutes (null = unlimited)')
    )
    passing_score_percentage = models.IntegerField(
        default=70,
        help_text=_('Minimum percentage to pass (0-100)')
    )
    max_attempts = models.IntegerField(
        blank=True,
        null=True,
        help_text=_('Maximum number of attempts (null = unlimited)')
    )
    shuffle_questions = models.BooleanField(
        default=True,
        help_text=_('Whether to randomize question order')
    )
    shuffle_answers = models.BooleanField(
        default=True,
        help_text=_('Whether to randomize answer order')
    )
    is_published = models.BooleanField(
        default=True,
        help_text=_('Whether the quiz is visible to students')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Quiz')
        verbose_name_plural = _('Quizzes')
        ordering = ['course', 'created_at']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    @property
    def total_questions(self):
        """Get total number of questions."""
        return self.questions.count()

    @property
    def total_points(self):
        """Get total possible points."""
        return sum(q.points for q in self.questions.all())


class Question(models.Model):
    """
    Individual question in a quiz.
    Supports multiple choice, true/false, and text answers.
    """
    class QuestionType(models.TextChoices):
        MULTIPLE_CHOICE = 'MC', _('Multiple Choice')
        TRUE_FALSE = 'TF', _('True/False')
        SHORT_ANSWER = 'SA', _('Short Answer')
        LONG_ANSWER = 'LA', _('Long Answer/Essay')

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    question_type = models.CharField(
        max_length=2,
        choices=QuestionType.choices,
        default=QuestionType.MULTIPLE_CHOICE
    )
    question_text = models.TextField(
        help_text=_('The question text')
    )
    explanation = models.TextField(
        blank=True,
        help_text=_('Explanation shown after answering')
    )
    points = models.IntegerField(
        default=1,
        help_text=_('Points awarded for correct answer')
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text=_('Display order within quiz')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')
        ordering = ['quiz', 'order']

    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}: {self.question_text[:50]}"


class Answer(models.Model):
    """
    Answer option for a question.
    For multiple choice questions, there can be multiple answers with one or more correct.
    """
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    answer_text = models.TextField(
        help_text=_('The answer text')
    )
    is_correct = models.BooleanField(
        default=False,
        help_text=_('Whether this is a correct answer')
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text=_('Display order')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Answer')
        verbose_name_plural = _('Answers')
        ordering = ['question', 'order']

    def __str__(self):
        return f"{self.question.question_text[:30]} - {self.answer_text[:30]}"


class QuizAttempt(models.Model):
    """
    A student's attempt at taking a quiz.
    """
    class Status(models.TextChoices):
        IN_PROGRESS = 'in_progress', _('In Progress')
        COMPLETED = 'completed', _('Completed')
        SUBMITTED = 'submitted', _('Submitted')

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_attempts',
        limit_choices_to={'role': 'STUDENT'}
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text=_('Score as percentage (0-100)')
    )
    points_earned = models.IntegerField(
        default=0,
        help_text=_('Total points earned')
    )
    points_possible = models.IntegerField(
        default=0,
        help_text=_('Total points possible')
    )
    time_taken_seconds = models.IntegerField(
        blank=True,
        null=True,
        help_text=_('Time taken to complete (in seconds)')
    )
    passed = models.BooleanField(
        default=False,
        help_text=_('Whether the student passed this attempt')
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('When the quiz was completed')
    )

    class Meta:
        verbose_name = _('Quiz Attempt')
        verbose_name_plural = _('Quiz Attempts')
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['student', 'quiz']),
        ]

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} ({self.score}%)"

    def calculate_score(self):
        """Calculate the score based on student responses."""
        total_points = 0
        earned_points = 0

        for response in self.responses.all():
            question = response.question
            total_points += question.points

            if response.is_correct:
                earned_points += question.points

        self.points_possible = total_points
        self.points_earned = earned_points

        if total_points > 0:
            self.score = (earned_points / total_points) * 100
        else:
            self.score = 0

        # Check if passed
        self.passed = self.score >= self.quiz.passing_score_percentage

        self.save()

    def submit(self):
        """Submit the quiz attempt and calculate final score."""
        from django.utils import timezone

        self.status = self.Status.SUBMITTED
        self.completed_at = timezone.now()

        # Calculate time taken
        if self.started_at and self.completed_at:
            time_diff = self.completed_at - self.started_at
            self.time_taken_seconds = int(time_diff.total_seconds())

        # Calculate score
        self.calculate_score()

        # Award points if passed
        if self.passed and hasattr(self.student, 'student_profile'):
            points = settings.SHIDOSHA_SETTINGS.get('POINTS_PER_QUIZ', 20)
            self.student.student_profile.add_points(points)

        self.save()


class QuestionResponse(models.Model):
    """
    A student's response to a quiz question.
    """
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='student_responses'
    )
    selected_answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='student_selections',
        help_text=_('For multiple choice questions')
    )
    text_answer = models.TextField(
        blank=True,
        help_text=_('For text answer questions')
    )
    is_correct = models.BooleanField(
        default=False,
        help_text=_('Whether the answer is correct (auto-graded for MC/TF)')
    )
    points_earned = models.IntegerField(
        default=0,
        help_text=_('Points earned for this response')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Question Response')
        verbose_name_plural = _('Question Responses')
        ordering = ['attempt', 'question']
        unique_together = ['attempt', 'question']

    def __str__(self):
        return f"{self.attempt.student.username} - {self.question.question_text[:30]}"

    def save(self, *args, **kwargs):
        # Auto-grade multiple choice and true/false
        if self.question.question_type in [Question.QuestionType.MULTIPLE_CHOICE, Question.QuestionType.TRUE_FALSE]:
            if self.selected_answer:
                self.is_correct = self.selected_answer.is_correct
                self.points_earned = self.question.points if self.is_correct else 0

        super().save(*args, **kwargs)
