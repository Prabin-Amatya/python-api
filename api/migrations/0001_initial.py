from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AppUser",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("display_name", models.CharField(max_length=120)),
                ("age", models.PositiveIntegerField()),
                ("job", models.CharField(max_length=120)),
                ("marital_status", models.CharField(max_length=50)),
                ("children", models.PositiveIntegerField(default=0)),
                ("gender", models.CharField(max_length=50)),
                ("income", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("hobbies_csv", models.TextField(blank=True, default="")),
                ("autism_level", models.FloatField(default=0)),
                ("adhd_level", models.FloatField(default=0)),
                ("other_neurological_conditions", models.TextField(blank=True, default="")),
                ("personality_type", models.CharField(blank=True, default="", max_length=50)),
                ("ocd_level", models.FloatField(default=0)),
                ("self_worth_tasks", models.BooleanField(default=False)),
                ("mother_relationship", models.CharField(blank=True, default="", max_length=100)),
                ("father_relationship", models.CharField(blank=True, default="", max_length=100)),
                ("bullied", models.BooleanField(default=False)),
                ("volatile_family", models.BooleanField(default=False)),
                ("clinically_depressed", models.BooleanField(default=False)),
                ("grief_impact", models.BooleanField(default=False)),
                ("reason_productive", models.CharField(max_length=50)),
                ("productivity_struggle", models.CharField(max_length=50)),
                ("comeback_plan", models.CharField(max_length=50)),
                ("morning_person", models.BooleanField(default=True)),
                ("total_tasks_started", models.PositiveIntegerField(default=0)),
                ("total_tasks_failed", models.PositiveIntegerField(default=0)),
                ("total_tasks_finished", models.PositiveIntegerField(default=0)),
                ("success_rate", models.FloatField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "app_users"},
        ),
        migrations.CreateModel(
            name="TaskEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("difficulty", models.PositiveIntegerField(default=1)),
                ("time_of_day", models.CharField(max_length=50)),
                ("day_of_week", models.CharField(max_length=20)),
                ("tasks_completed_before", models.PositiveIntegerField(default=0)),
                ("rest_taken_before", models.PositiveIntegerField(default=0)),
                ("previous_activity", models.CharField(blank=True, default="", max_length=120)),
                ("task_success", models.BooleanField(default=False)),
                ("productivity_drop", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="task_events",
                        to="api.appuser",
                    ),
                ),
            ],
            options={"db_table": "task_events"},
        ),
        migrations.CreateModel(
            name="UserHabit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("description", models.TextField(blank=True, default="")),
                ("success_rate", models.FloatField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="habits",
                        to="api.appuser",
                    ),
                ),
            ],
            options={"db_table": "user_habits"},
        ),
        migrations.CreateModel(
            name="SimilarityScore",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("score", models.FloatField()),
                ("rank", models.PositiveIntegerField(default=1)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "source_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="similarities_from",
                        to="api.appuser",
                    ),
                ),
                (
                    "target_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="similarities_to",
                        to="api.appuser",
                    ),
                ),
            ],
            options={
                "db_table": "similarity_scores",
                "ordering": ["source_user_id", "rank", "-score"],
                "unique_together": {("source_user", "target_user")},
            },
        ),
    ]
