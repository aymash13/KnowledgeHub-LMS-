from django.urls import path
from . import views

urlpatterns=[
    path('register/', views.RegisterView, name='register'),
    path('login/', views.LoginView, name='login'),
    path('logout/', views.logoutView, name='logout'),

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('ta-dashboard/', views.ta_dashboard, name='ta_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
]