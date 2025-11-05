from django.contrib import admin
from .models import UserTable

@admin.register(UserTable)
class UserTableAdmin(admin.ModelAdmin):
    list_display=("user","role")
    list_filter = ("role",)
    search_fields = ("user__username","user__email",)
