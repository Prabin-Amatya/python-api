from django.db import models


class Login(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "login"

    def __str__(self):
        return f"{self.username}"


class AppUser(models.Model):
    userid = models.OneToOneField(Login, on_delete=models.CASCADE, related_name="app_profile", db_column="userid", null=True, blank=True)
    display_name = models.CharField(max_length=120)
    age = models.PositiveIntegerField()
    job = models.CharField(max_length=120)
    marital_status = models.CharField(max_length=50)
    children = models.PositiveIntegerField(default=0)
    gender = models.CharField(max_length=50)
    income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    hobbies_csv = models.TextField(blank=True, default="")
    autism_level = models.FloatField(default=0)
    adhd_level = models.FloatField(default=0)
    other_neurological_conditions = models.TextField(blank=True, default="")
    personality_type = models.CharField(max_length=50, blank=True, default="")
    ocd_level = models.FloatField(default=0)
    self_worth_tasks = models.BooleanField(default=False)
    mother_relationship = models.CharField(max_length=100, blank=True, default="")
    father_relationship = models.CharField(max_length=100, blank=True, default="")
    bullied = models.BooleanField(default=False)
    volatile_family = models.BooleanField(default=False)
    clinically_depressed = models.BooleanField(default=False)
    grief_impact = models.BooleanField(default=False)
    reason_productive = models.CharField(max_length=50)
    productivity_struggle = models.CharField(max_length=50)
    comeback_plan = models.CharField(max_length=50)
    morning_person = models.BooleanField(default=True)
    total_tasks_started = models.PositiveIntegerField(default=0)
    total_tasks_failed = models.PositiveIntegerField(default=0)
    total_tasks_finished = models.PositiveIntegerField(default=0)
    success_rate = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "app_users"

    def __str__(self):
        return f"{self.display_name} ({self.id})"


class UserHabit(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name="habits")
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True, default="")
    success_rate = models.FloatField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_habits"

    def __str__(self):
        return f"{self.user_id}: {self.name}"


class TaskEvent(models.Model):
    user = models.ForeignKey(Login, on_delete=models.CASCADE, related_name="task_events", db_column="user")
    title = models.CharField(max_length=255)
    difficulty = models.PositiveIntegerField(default=1)
    time_of_day = models.CharField(max_length=50)
    day_of_week = models.CharField(max_length=20)
    tasks_completed_before = models.PositiveIntegerField(default=0)
    rest_taken_before = models.PositiveIntegerField(default=0)
    previous_activity = models.CharField(max_length=120, blank=True, default="")
    task_success = models.BooleanField(default=False)
    productivity_drop = models.BooleanField(default=False)
    STATUS_CHOICES = [
        ("PENDING", "PENDING"),
        ("FINISHED", "FINISHED"),
        ("NOT FINISHED", "NOT FINISHED"),
        ("SKIPPED", "SKIPPED"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    task_start_time = models.TimeField(null=True, blank=True)
    task_end_time = models.TimeField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "task_events"

    def __str__(self):
        return f"{self.user_id}: {self.title}"


class SimilarityScore(models.Model):
    source_user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name="similarities_from")
    target_user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name="similarities_to")
    score = models.FloatField()
    rank = models.PositiveIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "similarity_scores"
        unique_together = ("source_user", "target_user")
        ordering = ["source_user_id", "rank", "-score"]

    def __str__(self):
        return f"{self.source_user_id} -> {self.target_user_id}: {self.score:.3f}"


class SubTask(models.Model):
    task = models.ForeignKey(TaskEvent, on_delete=models.CASCADE, related_name="subtasks")
    task_desc = models.TextField()
    finished = models.CharField(max_length=50, default="False")
    createddatetime = models.DateTimeField(auto_now_add=True)
    finisheddatetime = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "subtasks"

    def __str__(self):
        return f"{self.task.title} - {self.task_desc[:20]}"


class Level(models.Model):
    level = models.PositiveIntegerField(unique=True)
    target = models.PositiveIntegerField()

    class Meta:
        db_table = "level_targets"
        ordering = ["level"]

    def __str__(self):
        return f"Level {self.level}: {self.target} XP"


class UserLevel(models.Model):
    user = models.OneToOneField(Login, on_delete=models.CASCADE, related_name="user_level", db_column="userid")
    level = models.PositiveIntegerField(default=1)
    exp = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "user_levels"

    def __str__(self):
        return f"{self.user.username} - Level {self.level} ({self.exp} XP)"

