from django.contrib import admin

from .models import AppUser, SimilarityScore, TaskEvent, UserHabit


@admin.register(AppUser)
class AppUserAdmin(admin.ModelAdmin):
    list_display = ("id", "display_name", "job", "reason_productive", "created_at")
    search_fields = ("display_name", "job", "reason_productive")


@admin.register(UserHabit)
class UserHabitAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "name", "success_rate", "is_active")
    search_fields = ("name",)


@admin.register(TaskEvent)
class TaskEventAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "day_of_week", "time_of_day", "task_success")
    search_fields = ("title", "previous_activity")


@admin.register(SimilarityScore)
class SimilarityScoreAdmin(admin.ModelAdmin):
    list_display = ("source_user", "target_user", "score", "rank", "updated_at")
    search_fields = ("source_user__display_name", "target_user__display_name")
