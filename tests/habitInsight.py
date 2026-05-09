import pandas as pd
import lightgbm as lgb
import json
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import shap

data = pd.DataFrame({
    "difficulty": [3, 5, 2, 7, 4, 6, 1],
    "time_of_day": ["morning", "afternoon", "morning", "evening", "afternoon", "morning", "evening"],
    "day_of_week": ["Mon", "Tue", "Wed", "Thu", "Fri", "Mon", "Sat"],
    "tasks_completed_before": [0, 2, 1, 4, 3, 1, 0],
    "rest_taken_before": [30, 10, 20, 5, 15, 25, 40],  # minutes
    "previous_activity": ["social_media", "reading", "social_media", "coding", "social_media", "reading", "coding"],
    "task_success": [1, 0, 1, 0, 0, 1, 1],
    "productivity_drop": [0, 1, 0, 1, 1, 0, 0]
})

categorical_features = ["time_of_day", "day_of_week", "previous_activity"]

for col in categorical_features:
    le = LabelEncoder()
    data[col] = le.fit_transform(data[col])

features = ["difficulty", "time_of_day", "day_of_week", "tasks_completed_before", "rest_taken_before", "previous_activity"]

X = data[features]
y_task = data["task_success"]
y_activity = data["productivity_drop"]


X_train_task, X_test_task, y_train_task, y_test_task = train_test_split(X, y_task, test_size=0.3, random_state=42)
X_train_act, X_test_act, y_train_act, y_test_act = train_test_split(X, y_activity, test_size=0.3, random_state=42)


task_model = lgb.LGBMClassifier(n_estimators=100, max_depth=5)
activity_model = lgb.LGBMClassifier(n_estimators=100, max_depth=5)

task_model.fit(X_train_task, y_train_task)
activity_model.fit(X_train_act, y_train_act)


explainer = shap.TreeExplainer(task_model)


def predict_task(json_input):
    df = pd.DataFrame([json_input])
    
    for col in categorical_features:
        df[col] = le.fit_transform(df[col])
    
    task_prob = task_model.predict_proba(df)[0][1]
    activity_prob = activity_model.predict_proba(df)[0][1]
    
    shap_values = explainer.shap_values(df)
    
    explanation = []
    for i, col in enumerate(features):
        if shap_values[0][0][i] < 0:
            explanation.append(f"{col.replace('_',' ')} reduces chance of success.")
        elif shap_values[0][0][i] > 0:
            explanation.append(f"{col.replace('_',' ')} increases chance of success.")
    
    if df["rest_taken_before"].values[0] < 20:
        explanation.append("You only had short rest before this activity, so it is likely to fail.")
    if df["tasks_completed_before"].values[0] > 5:
        explanation.append("You completed many tasks before, fatigue may reduce success.")
    
    return {
        "task_success_probability": round(task_prob,2),
        "productivity_drop_probability": round(activity_prob,2),
        "explanation": explanation
    }


example_json = {
    "difficulty": 5,
    "time_of_day": "afternoon",
    "day_of_week": "Wed",
    "tasks_completed_before": 3,
    "rest_taken_before": 15,
    "previous_activity": "social_media"
}

result = predict_task(example_json)
print(json.dumps(result, indent=4))