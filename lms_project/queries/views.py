from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Query
from .forms import QueryForm

# -----------------------------
# STUDENT VIEWS
# -----------------------------
@login_required
def query_list(request):
    """List all queries visible to the current user."""
    user = request.user
    role = user.usertable.role

    if role == "STUDENT":
        queries = Query.objects.filter(created_by=user)
    elif role in ["TEACHER", "TA"]:
        queries = Query.objects.filter(assigned_to=user) | Query.objects.filter(status="Open")
    else:
        queries = Query.objects.all()

    return render(request, "queries/query_list.html", {"queries": queries})


@login_required
def query_create(request):
    """Allow students to create a new query."""
    if request.user.usertable.role != "STUDENT":
        messages.error(request, "Only students can create queries.")
        return redirect("query_list")

    if request.method == "POST":
        form = QueryForm(request.POST)
        if form.is_valid():
            query = form.save(commit=False)
            query.created_by = request.user
            query.status = "Open"
            query.save()
            messages.success(request, "Your query has been submitted successfully.")
            return redirect("query_list")
    else:
        form = QueryForm()

    return render(request, "queries/query_form.html", {"form": form})


@login_required
def query_detail(request, query_id):
    """View and interact with a single query."""
    query = get_object_or_404(Query, id=query_id)

    if request.method == "POST":
        # TEACHER/TA updates response
        if request.user.usertable.role in ["TEACHER", "TA"]:
            query.response = request.POST.get("response")
            query.status = request.POST.get("status")
            query.save()
            messages.success(request, "Response updated successfully.")

        # STUDENT replies or resolves
        elif request.user.usertable.role == "STUDENT":
            action = request.POST.get("action")
            student_reply = request.POST.get("student_reply")

            if action == "reply" and student_reply:
                query.response = (query.response or "") + f"\n\n[Student Reply]: {student_reply}"
                query.status = "In Progress"
                query.save()
                messages.success(request, "Your reply has been sent.")
            elif action == "resolve":
                query.status = "Resolved"
                query.save()
                messages.success(request, "Query marked as resolved.")

        return redirect("query_detail", query_id=query.id)

    return render(request, "queries/query_detail.html", {"query": query})