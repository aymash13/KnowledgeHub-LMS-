from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, LoginForm
from .models import UserTable


# use for redirect based on user role
def redirect_dashboard(role):
    if role == "ADMIN":
        return redirect("admin_dashboard")
    elif role == "TEACHER":
        return redirect("teacher_dashboard")
    elif role == "TA":
        return redirect("ta_dashboard")
    else:
        return redirect("student_dashboard")


# REGISTER VIEW
def RegisterView(request):
    if request.user.is_authenticated:
        return redirect_dashboard(request.user.usertable.role)

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data.get("email")
            user.save()

            role = form.cleaned_data.get("role")
            # Create or update the UserTable entry for this user
            UserTable.objects.update_or_create(user=user, defaults={'role': role})

            messages.success(request, f"Account created for {user.username} as {role}. Please login.")
            return redirect("login")
        else:
            messages.error(request, "There was an error with your registration. Please check the details.")
    else:
        form = UserRegisterForm()

    return render(request, "accounts/register.html", {"form": form})


# LOGIN VIEW 
def LoginView(request):
    if request.user.is_authenticated:
        return redirect_dashboard(request.user.usertable.role)

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect_dashboard(user.usertable.role)
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid form submission. Please try again.")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


#  LOGOUT VIEW
def logoutView(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")


# DASHBOARD VIEWS
@login_required
def admin_dashboard(request):
    return render(request, 'accounts/admin_dashboard.html')

@login_required
def teacher_dashboard(request):
    return render(request, 'accounts/teacher_dashboard.html')

@login_required
def ta_dashboard(request):
    return render(request, 'accounts/ta_dashboard.html')

@login_required
def student_dashboard(request):
    return render(request, 'accounts/student_dashboard.html')