# AR Productivity API

This repo now includes a Django API layer for your Unity AR productivity app.

## Endpoints

- `POST /api/tasks/breakdown/`
- `GET /api/users/<user_id>/habit-insight/`
- `POST /api/users/register/`
- `POST /api/similarity/recompute/`
- `GET /api/users/<user_id>/similar-users/`
- `POST /api/users/<user_id>/task-events/`

## SQL Server

Configured for:

- Server: `DESKTOP-4QC4A32\SQLEXPRESS`
- Database: `ArProd`
- Trusted connection
- Trust server certificate enabled

## Example setup

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Register user payload

```json
{
  "display_name": "Aayush",
  "age": 24,
  "job": "student",
  "marital_status": "single",
  "children": 0,
  "gender": "male",
  "income": 0,
  "hobbies": ["coding", "music", "gaming"],
  "autism_level": 0.2,
  "adhd_level": 0.1,
  "other_neurological_conditions": "none",
  "personality_type": "INTJ",
  "ocd_level": 0.0,
  "self_worth_tasks": true,
  "mother_relationship": "absent_but_in_life",
  "father_relationship": "loving",
  "bullied": true,
  "volatile_family": false,
  "clinically_depressed": false,
  "grief_impact": false,
  "reason_productive": "genuine_interest",
  "productivity_struggle": "i_get_most_things_done_but_struggle_sometimes",
  "comeback_plan": "yes",
  "morning_person": true,
  "total_tasks_started": 20,
  "total_tasks_failed": 6,
  "total_tasks_finished": 14,
  "habits": [
    {
      "name": "Morning walk",
      "description": "10 minute walk after waking up",
      "success_rate": 0.85,
      "is_active": true
    }
  ]
}
```
