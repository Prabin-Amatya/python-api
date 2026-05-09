from collections import defaultdict

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

try:
    import lightgbm as lgb
except ImportError:  # pragma: no cover
    lgb = None

try:
    import shap
except ImportError:  # pragma: no cover
    shap = None

from api.models import TaskEvent


def _rate_summary(records, bucket_field):
    totals = defaultdict(lambda: {"success": 0, "fail": 0})
    for record in records:
        bucket = getattr(record, bucket_field)
        if record.task_success:
            totals[bucket]["success"] += 1
        else:
            totals[bucket]["fail"] += 1

    summary = []
    for bucket, counts in totals.items():
        total = counts["success"] + counts["fail"]
        summary.append(
            {
                bucket_field: bucket,
                "success": counts["success"],
                "fail": counts["fail"],
                "success_rate": round((counts["success"] / total) if total else 0, 3),
            }
        )
    summary.sort(key=lambda item: item["success_rate"], reverse=True)
    return summary


def _build_explanation(model, row, feature_names):
    if shap is None:
        return []

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(row)

    if isinstance(shap_values, list):
        values = shap_values[0][0]
    else:
        values = shap_values[0]

    explanation = []
    for index, feature in enumerate(feature_names):
        if values[index] > 0:
            explanation.append(f"{feature.replace('_', ' ')} increases the chance of success.")
        elif values[index] < 0:
            explanation.append(f"{feature.replace('_', ' ')} decreases the chance of success.")
    return explanation


def get_habit_insight(user_id):
    records = list(TaskEvent.objects.filter(user_id=user_id).order_by("created_at"))
    if not records:
        return {
            "user_id": user_id,
            "message": "No task history found for this user.",
            "best_days": [],
            "worst_days": [],
            "best_times": [],
            "worst_times": [],
        }

    day_summary = _rate_summary(records, "day_of_week")
    time_summary = _rate_summary(records, "time_of_day")

    if lgb is None or len(records) < 6:
        return {
            "user_id": user_id,
            "message": "Insight generated from historical rates because there is not enough data to train LightGBM yet.",
            "best_days": day_summary[:3],
            "worst_days": list(reversed(day_summary[-3:])),
            "best_times": time_summary[:3],
            "worst_times": list(reversed(time_summary[-3:])),
        }

    frame = pd.DataFrame(
        [
            {
                "difficulty": record.difficulty,
                "time_of_day": record.time_of_day,
                "day_of_week": record.day_of_week,
                "tasks_completed_before": record.tasks_completed_before,
                "rest_taken_before": record.rest_taken_before,
                "previous_activity": record.previous_activity,
                "task_success": int(record.task_success),
                "productivity_drop": int(record.productivity_drop),
            }
            for record in records
        ]
    )

    feature_names = [
        "difficulty",
        "time_of_day",
        "day_of_week",
        "tasks_completed_before",
        "rest_taken_before",
        "previous_activity",
    ]
    categorical_features = ["time_of_day", "day_of_week", "previous_activity"]
    for column in categorical_features:
        encoder = LabelEncoder()
        frame[column] = encoder.fit_transform(frame[column])

    X = frame[feature_names]
    y_success = frame["task_success"]
    y_drop = frame["productivity_drop"]

    X_train_success, _, y_train_success, _ = train_test_split(
        X, y_success, test_size=0.3, random_state=42
    )
    X_train_drop, _, y_train_drop, _ = train_test_split(
        X, y_drop, test_size=0.3, random_state=42
    )

    success_model = lgb.LGBMClassifier(n_estimators=100, max_depth=5)
    drop_model = lgb.LGBMClassifier(n_estimators=100, max_depth=5)
    success_model.fit(X_train_success, y_train_success)
    drop_model.fit(X_train_drop, y_train_drop)

    latest_row = X.tail(1)
    latest_source = records[-1]
    explanation = _build_explanation(success_model, latest_row, feature_names)
    if latest_source.rest_taken_before < 20:
        explanation.append("Short rest before a task is a recurring risk signal for this user.")
    if latest_source.tasks_completed_before > 5:
        explanation.append("High workload before the current task suggests fatigue may reduce success.")

    return {
        "user_id": user_id,
        "latest_context": {
            "day_of_week": latest_source.day_of_week,
            "time_of_day": latest_source.time_of_day,
            "difficulty": latest_source.difficulty,
        },
        "task_success_probability": round(float(success_model.predict_proba(latest_row)[0][1]), 3),
        "productivity_drop_probability": round(float(drop_model.predict_proba(latest_row)[0][1]), 3),
        "best_days": day_summary[:3],
        "worst_days": list(reversed(day_summary[-3:])),
        "best_times": time_summary[:3],
        "worst_times": list(reversed(time_summary[-3:])),
        "explanation": explanation,
    }
