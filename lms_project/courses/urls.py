from django.urls import path
from . import views

urlpatterns = [
    # Dashboards
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),

    # Course + Lessons
    path('', views.course_list, name='course_list'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('course/<int:course_id>/lesson/<int:lesson_id>/', views.lesson_view, name='lesson_view'),

    # Teacher Actions
    path('create-course/', views.create_course, name='create_course'),
    path('course/<int:course_id>/create-lesson/', views.create_lesson, name='create_lesson'),

    # Quiz Functionality
    path('course/<int:course_id>/create-quiz/', views.create_quiz, name='create_quiz'),
    path('quiz/<int:quiz_id>/add-question/', views.add_question, name='add_question'),
    path('quiz/<int:quiz_id>/attempt/', views.attempt_quiz, name='attempt_quiz'),
]