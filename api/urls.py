from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.health_check, name="health-check"),
    path("tasks/breakdown/", views.break_down_task, name="break-down-task"),
    path("users/register/", views.register_user, name="register-user"),
    path("users/<int:user_id>/task-events/", views.create_task_event, name="create-task-event"),
    path("users/<int:user_id>/task-events/list/", views.list_task_events, name="list-task-events"),
    path("users/<int:user_id>/task-events/<int:event_id>/", views.task_event_detail, name="task-event-detail"),
    path("users/<int:user_id>/habit-insight/", views.habit_insight, name="habit-insight"),
    path("similarity/recompute/", views.recompute_similarity, name="recompute-similarity"),
    path("users/<int:user_id>/similar-users/", views.similar_users, name="similar-users"),
    path("users/login/", views.user_login, name="user-login"),
    path("registeruser/", views.register_login_only, name="register-login-only"),
    path("login/", views.verify_login, name="verify-login"),
]
