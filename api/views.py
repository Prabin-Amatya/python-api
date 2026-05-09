import json

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from .services.habit_insight import get_habit_insight
from .services.similarity import get_similar_users_with_habits, recompute_similarity_matrix
from .services.task_breakdown import generate_subtasks
from .models import AppUser, TaskEvent, UserHabit, Login, SubTask, Level, UserLevel
from rest_framework.decorators import api_view
from rest_framework.response import Response

def _parse_json(request: HttpRequest):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return None

def _update_success_rate(user: AppUser):
    finished = user.total_tasks_finished
    failed = user.total_tasks_failed
    started = user.total_tasks_started
    if finished <= 0 or started <= 0:
        user.success_rate = 0
    else:
        completion_rate = started / finished if finished else 0
        failure_rate = failed / finished if finished else 0
        user.success_rate = round(completion_rate / max(failure_rate, 1), 4)


def ensure_levels_populated():
    if not Level.objects.exists():
        levels = [Level(level=i, target=i * 10) for i in range(1, 101)]
        Level.objects.bulk_create(levels)


def get_user_level_data(user_login):
    ul, _ = UserLevel.objects.get_or_create(user=user_login)
    target_xp = 100 # Default fallback
    try:
        level_obj = Level.objects.get(level=ul.level)
        target_xp = level_obj.target
    except Level.DoesNotExist:
        target_xp = ul.level * 10
    
    return {
        "level": ul.level,
        "exp": ul.exp,
        "target_exp": target_xp
    }


@api_view(['GET'])
def health_check(_request):
    ensure_levels_populated()
    return JsonResponse({"status": "ok"})


@csrf_exempt
@api_view(['GET'])
def break_down_task(request: HttpRequest):
    payload = _parse_json(request)
    if payload is None:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    main_task = (payload.get("main_task") or "").strip()
    if not main_task:
        return JsonResponse({"error": "main_task is required."}, status=400)

    return JsonResponse(generate_subtasks(main_task))


@csrf_exempt
@api_view(['POST'])
def register_user(request: HttpRequest):
    payload = _parse_json(request)
    if payload is None:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    habits_payload = payload.pop("habits", [])
    hobbies = payload.pop("hobbies", [])
    login_payload = payload.pop("login", None)

    login_obj = None
    login_id = payload.pop("login_id", None)
    if login_payload:
        login_obj = Login.objects.create(
            username=login_payload.get("username"),
            password=login_payload.get("password"),
            email=login_payload.get("email")
        )
    elif login_id:
        try:
            login_obj = Login.objects.get(id=login_id)
        except Login.DoesNotExist:
            return JsonResponse({"error": "Login not found."}, status=404)

    user = AppUser.objects.create(
        userid=login_obj,
        display_name=payload.get("display_name", "Unnamed User"),
        age=payload.get("age", 0),
        job=payload.get("job", ""),
        marital_status=payload.get("marital_status", ""),
        children=payload.get("children", 0),
        gender=payload.get("gender", ""),
        income=payload.get("income", 0),
        hobbies_csv=",".join(hobbies),
        autism_level=payload.get("autism_level", 0),
        adhd_level=payload.get("adhd_level", 0),
        other_neurological_conditions=payload.get("other_neurological_conditions", ""),
        personality_type=payload.get("personality_type", ""),
        ocd_level=payload.get("ocd_level", 0),
        self_worth_tasks=payload.get("self_worth_tasks", False),
        mother_relationship=payload.get("mother_relationship", ""),
        father_relationship=payload.get("father_relationship", ""),
        bullied=payload.get("bullied", False),
        volatile_family=payload.get("volatile_family", False),
        clinically_depressed=payload.get("clinically_depressed", False),
        grief_impact=payload.get("grief_impact", False),
        reason_productive=payload.get("reason_productive", ""),
        productivity_struggle=payload.get("productivity_struggle", ""),
        comeback_plan=payload.get("comeback_plan", ""),
        morning_person=payload.get("morning_person", True),
        total_tasks_started=payload.get("total_tasks_started", 0),
        total_tasks_failed=payload.get("total_tasks_failed", 0),
        total_tasks_finished=payload.get("total_tasks_finished", 0),
    )
    _update_success_rate(user)
    user.save(update_fields=["success_rate"])

    for habit in habits_payload:
        UserHabit.objects.create(
            user=user,
            name=habit.get("name", ""),
            description=habit.get("description", ""),
            success_rate=habit.get("success_rate", 0),
            is_active=habit.get("is_active", True),
        )

    recompute_similarity_matrix()

    return JsonResponse(
        {
            "message": "User registered and similarity matrix recalculated.",
            "user_id": user.id,
        },
        status=201,
    )


@csrf_exempt
@api_view(['POST'])
def create_task_event(request: HttpRequest, user_id: int):
    payload = _parse_json(request)
    if payload is None:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    try:
        user_profile = AppUser.objects.get(userid_id=user_id)
    except AppUser.DoesNotExist:
        user_profile = None

    task_event = TaskEvent.objects.create(
        user_id=user_id,
        title=payload.get("title", ""),
        difficulty=payload.get("difficulty", 1),
        time_of_day=payload.get("time_of_day", ""),
        day_of_week=payload.get("day_of_week", ""),
        tasks_completed_before=payload.get("tasks_completed_before", 0),
        rest_taken_before=payload.get("rest_taken_before", 0),
        previous_activity=payload.get("previous_activity", ""),
        task_success=payload.get("task_success", False),
        productivity_drop=payload.get("productivity_drop", False),
        task_start_time=payload.get("task_start_time"),
        task_end_time=payload.get("task_end_time"),
        latitude=payload.get("latitude"),
        longitude=payload.get("longitude"),
    )

    if user_profile:
        user_profile.total_tasks_started += 1
        if task_event.task_success:
            user_profile.total_tasks_finished += 1
        else:
            user_profile.total_tasks_failed += 1
        user_profile.save(update_fields=["total_tasks_started", "total_tasks_finished", "total_tasks_failed"])
    
    # 5. Generate and save subtasks
    try:
        breakdown = generate_subtasks(task_event.title)
        for st_data in breakdown.get("sub_tasks", []):
            SubTask.objects.create(
                task=task_event,
                task_desc=st_data.get("name", "Unnamed Subtask"),
                finished="False"
            )
    except Exception as e:
        print(f"Error generating subtasks: {e}")

    return JsonResponse({"message": "Task event saved with subtasks.", "task_event_id": task_event.id}, status=201)


@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def task_event_detail(request: HttpRequest, user_id: int, event_id: int):
    try:
        event = TaskEvent.objects.get(id=event_id, user_id=user_id)
    except TaskEvent.DoesNotExist:
        return JsonResponse({"error": "Task event not found."}, status=404)

    if request.method == 'GET':
        subtasks = event.subtasks.all()
        return JsonResponse({
            "id": event.id,
            "title": event.title,
            "difficulty": event.difficulty,
            "task_success": event.task_success,
            "time_of_day": event.time_of_day,
            "day_of_week": event.day_of_week,
            "status": event.status,
            "task_start_time": event.task_start_time.strftime("%H:%M") if event.task_start_time else None,
            "task_end_time": event.task_end_time.strftime("%H:%M") if event.task_end_time else None,
            "latitude": event.latitude,
            "longitude": event.longitude,
            "subtasks": [
                {
                    "id": s.id,
                    "task_desc": s.task_desc,
                    "finished": s.finished
                } for s in subtasks
            ]
        })

    user = event.user
    if request.method == 'PUT':
        payload = _parse_json(request)
        if payload is None:
            return JsonResponse({"error": "Invalid JSON body."}, status=400)

        # Reverse previous impact
        app_user = getattr(event.user, 'app_profile', None)
        if app_user:
            if event.task_success:
                app_user.total_tasks_finished -= 1
            else:
                app_user.total_tasks_failed -= 1
        
        # Update fields
        event.title = payload.get("title", event.title)
        event.difficulty = payload.get("difficulty", event.difficulty)
        event.task_success = payload.get("task_success", event.task_success)
        event.status = payload.get("status", event.status)
        event.save()

        # Apply impact only for terminal statuses
        if app_user and event.status in ["FINISHED", "NOT FINISHED", "SKIPPED"]:
            if event.task_success:
                app_user.total_tasks_finished += 1
            else:
                app_user.total_tasks_failed += 1
            
            _update_success_rate(app_user)
            app_user.save(update_fields=["total_tasks_finished", "total_tasks_failed", "success_rate"])

        # Leveling logic
        if event.status == "FINISHED":
            ul, _ = UserLevel.objects.get_or_create(user=event.user)
            ul.exp += 5
            
            # Ensure levels are populated if they went missing
            if not Level.objects.exists():
                ensure_levels_populated()
                
            try:
                # Check for level up
                while True:
                    level_obj = Level.objects.get(level=ul.level)
                    if ul.exp >= level_obj.target:
                        ul.level += 1
                        ul.exp = 0 # Reset XP as requested
                    else:
                        break
            except Level.DoesNotExist:
                pass
            ul.save()

        return JsonResponse({
            "message": "Task event updated.",
            "level_data": get_user_level_data(event.user)
        })

    if request.method == 'DELETE':
        if event.task_success:
            user.total_tasks_finished -= 1
        else:
            user.total_tasks_failed -= 1
        user.total_tasks_started -= 1
        
        event.delete()
        
        _update_success_rate(user)
        user.save(update_fields=["total_tasks_started", "total_tasks_finished", "total_tasks_failed", "success_rate"])
        return JsonResponse({"message": "Task event deleted."})


@api_view(['GET'])
def list_task_events(request: HttpRequest, user_id: int):
    events = TaskEvent.objects.filter(user_id=user_id, status="PENDING").order_by("-created_at")
    results = []
    for e in events:
        results.append({
            "id": e.id,
            "title": e.title,
            "difficulty": e.difficulty,
            "task_success": e.task_success,
            "time_of_day": e.time_of_day,
            "day_of_week": e.day_of_week,
            "status": e.status,
            "task_start_time": e.task_start_time.strftime("%H:%M") if e.task_start_time else None,
            "task_end_time": e.task_end_time.strftime("%H:%M") if e.task_end_time else None,
            "latitude": e.latitude,
            "longitude": e.longitude,
        })
        
    level_data = None
    try:
        ul = UserLevel.objects.get(user_id=user_id)
        try:
            target = Level.objects.get(level=ul.level).target
        except Level.DoesNotExist:
            target = ul.level * 10
        level_data = {"level": ul.level, "exp": ul.exp, "target_exp": target}
    except UserLevel.DoesNotExist:
        level_data = {"level": 1, "exp": 0, "target_exp": 10}

    return JsonResponse({"events": results, "level_data": level_data})

@api_view(['GET'])
def habit_insight(_request: HttpRequest, user_id: int):
    return JsonResponse(get_habit_insight(user_id))


@csrf_exempt
@api_view(['POST'])
def recompute_similarity(_request: HttpRequest):
    recompute_similarity_matrix()
    return JsonResponse({"message": "Similarity matrix recomputed successfully."})


@api_view(['GET'])
def similar_users(request: HttpRequest, user_id: int):
    limit = int(request.GET.get("limit", 5))
    return JsonResponse(
        {
            "user_id": user_id,
            "results": get_similar_users_with_habits(user_id, limit=limit),
        }
    )


@csrf_exempt
@api_view(['POST'])
def user_login(request: HttpRequest):
    payload = _parse_json(request)
    if payload is None:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    username = payload.get("username")
    password = payload.get("password")

    if not username or not password:
        return JsonResponse({"error": "Username and password are required."}, status=400)

    try:
        # Normal login to verify users
        login_obj = Login.objects.get(username=username, password=password)
        # Use the related name 'app_profile' to get the user
        user = login_obj.app_profile
        return JsonResponse({
            "message": "Login successful.",
            "user_id": user.id,
            "display_name": user.display_name,
            "level_data": get_user_level_data(login_obj)
        }, status=200)
    except Login.DoesNotExist:
        return JsonResponse({"error": "Invalid credentials."}, status=401)
    except AppUser.DoesNotExist:
        return JsonResponse({"error": "Login successful but no user profile found."}, status=404)


@csrf_exempt
@api_view(['POST'])
def register_login_only(request: HttpRequest):
    payload = _parse_json(request)
    if not payload:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    username = payload.get("username")
    password = payload.get("password")
    email = payload.get("email", "")

    if not username or not password:
        return JsonResponse({"error": "Username and password are required."}, status=400)

    if Login.objects.filter(username=username).exists():
        return JsonResponse({"error": "Username already exists."}, status=400)

    login_obj = Login.objects.create(
        username=username,
        password=password,
        email=email
    )
    return JsonResponse({"message": "User registered successfully", "userid": login_obj.id}, status=201)


@csrf_exempt
@api_view(['POST'])
def verify_login(request: HttpRequest):
    payload = _parse_json(request)
    if not payload:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    username = payload.get("username")
    password = payload.get("password")

    try:
        login_obj = Login.objects.get(username=username, password=password)
        
        level_data = None
        try:
            ul = UserLevel.objects.get(user_id=login_obj.id)
            try:
                target = Level.objects.get(level=ul.level).target
            except Level.DoesNotExist:
                target = ul.level * 10
            level_data = {"level": ul.level, "exp": ul.exp, "target_exp": target}
        except UserLevel.DoesNotExist:
            level_data = {"level": 1, "exp": 0, "target_exp": 10}
            
        return JsonResponse({"message": "Login successful", "userid": login_obj.id, "level_data": level_data}, status=200)
    except Login.DoesNotExist:
        return JsonResponse({"error": "Invalid username or password"}, status=401)
