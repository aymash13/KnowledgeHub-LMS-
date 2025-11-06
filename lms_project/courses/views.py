from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from .models import Course, Lesson, Enrollment, Quiz, Question
from .forms import CourseForm, LessonForm, QuizForm, QuestionForm


# ---- Role Check Decorator ----
def teacher_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'usertable') or request.user.usertable.role != 'TEACHER':
            return HttpResponseForbidden("Access denied: Teacher only.")
        return view_func(request, *args, **kwargs)
    return wrapper


# ---------------------- STUDENT DASHBOARD ----------------------
@login_required
def student_dashboard(request):
    """Display all available courses with enrollment status."""
    if not hasattr(request.user, 'usertable') or request.user.usertable.role != 'STUDENT':
        return HttpResponseForbidden("Access denied: Students only.")
    
    courses = Course.objects.all().order_by('-created_at')
    enrolled_ids = Enrollment.objects.filter(student=request.user).values_list('course_id', flat=True)

    return render(request, 'accounts/student_dashboard.html', {
        'courses': courses,
        'enrolled_ids': list(enrolled_ids)
    })


# ---------------------- Public / Student Views ----------------------

def course_list(request):
    courses = Course.objects.all().order_by('-created_at')
    return render(request, 'courses/course_list.html', {'courses': courses})


def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    user_enrolled = False
    if request.user.is_authenticated:
        user_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    lessons = course.lessons.all().order_by('order')
    quizzes = course.quizzes.all()
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'lessons': lessons,
        'quizzes': quizzes,
        'user_enrolled': user_enrolled
    })


@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.user.usertable.role != 'STUDENT':
        messages.error(request, "Only students can enroll.")
        return redirect('course_detail', course_id=course.id)

    enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)
    if created:
        messages.success(request, f'You have successfully enrolled in {course.title}.')
    else:
        messages.info(request, 'You are already enrolled in this course.')
    return redirect('student_dashboard')


@login_required
def my_courses(request):
    if request.user.usertable.role == 'STUDENT':
        enrollments = Enrollment.objects.filter(student=request.user)
        return render(request, 'courses/my_courses_student.html', {'enrollments': enrollments})
    elif request.user.usertable.role == 'TEACHER':
        courses = Course.objects.filter(teacher=request.user).order_by('-created_at')
        return render(request, 'courses/my_courses_teacher.html', {'courses': courses})
    else:
        messages.info(request, "No courses available for your role.")
        return redirect('course_list')


@login_required
def lesson_view(request, course_id, lesson_id):
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)

    if request.user.usertable.role == 'STUDENT' and not Enrollment.objects.filter(student=request.user, course=course).exists():
        return HttpResponseForbidden("You must enroll to view this lesson.")
    if request.user.usertable.role == 'TEACHER' and course.teacher != request.user:
        return HttpResponseForbidden("Access denied: Not your course.")

    return render(request, 'courses/lesson_view.html', {'course': course, 'lesson': lesson})


# ---------------------- Teacher Views ----------------------

@teacher_required
def teacher_dashboard(request):
    courses = Course.objects.filter(teacher=request.user).order_by('-created_at')
    return render(request, 'accounts/teacher_dashboard.html', {'courses': courses})


@teacher_required
def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            messages.success(request, 'Course created successfully.')
            return redirect('teacher_dashboard')
    else:
        form = CourseForm()
    return render(request, 'courses/create_course.html', {'form': form})


@teacher_required
def create_lesson(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if course.teacher != request.user:
        return HttpResponseForbidden("Access denied: Not your course.")

    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            messages.success(request, 'Lesson added successfully.')
            return redirect('course_detail', course_id=course.id)
    else:
        form = LessonForm()

    return render(request, 'courses/create_lesson.html', {'form': form, 'course': course})


@teacher_required
def create_quiz(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if course.teacher != request.user:
        return HttpResponseForbidden("Access denied: Not your course.")

    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.course = course
            quiz.created_by = request.user
            quiz.save()
            messages.success(request, 'Quiz created successfully. You can now add questions.')
            return redirect('add_question', quiz_id=quiz.id)
    else:
        form = QuizForm()

    return render(request, 'courses/create_quiz.html', {'form': form, 'course': course})


@teacher_required
def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if quiz.created_by != request.user:
        return HttpResponseForbidden("Access denied: Not your quiz.")

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(request, 'Question added successfully.')
            return redirect('add_question', quiz_id=quiz.id)
    else:
        form = QuestionForm()

    questions = quiz.questions.all()
    return render(request, 'courses/add_question.html', {'form': form, 'quiz': quiz, 'questions': questions})


# ---------------------- Student: Attempt Quiz ----------------------

@login_required
def attempt_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    course = quiz.course

    if request.user.usertable.role != 'STUDENT' or not Enrollment.objects.filter(student=request.user, course=course).exists():
        return HttpResponseForbidden("You must be an enrolled student to attempt this quiz.")

    questions = quiz.questions.all()

    if request.method == 'POST':
        correct = 0
        total = questions.count()
        for q in questions:
            key = f"q_{q.id}"
            selected = request.POST.get(key)
            if selected == q.correct_option:
                correct += 1

        score = correct
        percent = (correct / total * 100) if total else 0

        return render(request, 'courses/quiz_result.html', {
            'quiz': quiz,
            'score': score,
            'total': total,
            'percent': percent
        })

    return render(request, 'courses/attempt_quiz.html', {'quiz': quiz, 'questions': questions})