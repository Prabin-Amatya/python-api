import json
import random

categories = {
    "Daily Life": [
        "Read a book", "Brush teeth", "Drink water", "Go for a walk", "Take a shower",
        "Wake up early", "Go to sleep", "Make bed", "Take medicine", "Meditate",
        "Eat breakfast", "Eat lunch", "Eat dinner", "Check phone messages", "Listen to music",
        "Call a friend", "Write a journal", "Pack bag", "Pay bills", "Plan day"
    ],
    "Study / Work": [
        "Study for exams", "Do homework", "Write a report", "Prepare presentation",
        "Learn programming", "Build a website", "Read research paper", "Write essay",
        "Prepare for interview", "Organize files", "Take notes", "Practice language",
        "Solve math problems", "Plan project", "Schedule meetings", "Review lecture notes",
        "Submit assignment", "Read textbook chapter", "Summarize article", "Plan study schedule"
    ],
    "Health / Fitness": [
        "Go to the gym", "Do push-ups", "Run 5 km", "Stretch", "Yoga session",
        "Cook healthy meal", "Track calories", "Drink water regularly", "Sleep 8 hours",
        "Check blood pressure", "Take vitamins", "Floss teeth", "Weight lifting",
        "Cycling", "Swim laps", "Go for hike", "Do meditation", "Practice breathing exercises",
        "Track steps", "Plan workout routine"
    ],
    "Home / Chores": [
        "Clean your room", "Wash dishes", "Do laundry", "Cook rice", "Cook pasta",
        "Vacuum floor", "Dust furniture", "Mop floor", "Organize wardrobe", "Take out trash",
        "Water plants", "Clean windows", "Clean fridge", "Sweep porch", "Organize pantry",
        "Fix leaky tap", "Paint a room", "Repair furniture", "Change light bulb", "Wash car"
    ],
    "Hobbies / Fun": [
        "Watch a movie", "Play guitar", "Play piano", "Draw a sketch", "Paint a canvas",
        "Read comics", "Play video game", "Write a story", "Do photography", "Practice chess",
        "Do knitting", "Build Lego set", "Bake cookies", "Learn magic trick", "Practice dance",
        "Go for photography walk", "Try new recipe", "Learn calligraphy", "Solve puzzles", "Write poem"
    ]
}

modifiers = ["", " today", " quickly", " carefully", " step by step", " efficiently", " with focus"]

def realistic_steps(task):
    templates = [
        f"1. Prepare for {task.lower()}\n2. Start {task.lower()}\n3. Focus on the main goal of {task.lower()}\n4. Take intermediate actions related to {task.lower()}\n5. Review progress during {task.lower()}\n6. Finalize {task.lower()}\n7. Conclude and reflect on {task.lower()}",
        f"1. Gather all materials needed for {task.lower()}\n2. Begin {task.lower()} carefully\n3. Follow the logical steps to complete {task.lower()}\n4. Monitor your performance in {task.lower()}\n5. Adjust approach if necessary\n6. Finish the core actions of {task.lower()}\n7. Review results of {task.lower()}",
        f"1. Plan how to {task.lower()}\n2. Set up environment for {task.lower()}\n3. Execute initial steps of {task.lower()}\n4. Continue tasks while maintaining focus\n5. Check quality of work in {task.lower()}\n6. Wrap up remaining actions\n7. Reflect and improve for next {task.lower()}"
    ]
    return random.choice(templates)

dataset = []

while len(dataset) < 5000:
    for cat_tasks in categories.values():
        for task in cat_tasks:
            # Apply random modifier
            modifier = random.choice(modifiers)
            task_variant = f"{task}{modifier}"
            dataset.append({
                "input": f"Break task into steps: {task_variant}",
                "output": realistic_steps(task_variant)
            })
            if len(dataset) >= 5000:
                break
        if len(dataset) >= 5000:
            break

random.shuffle(dataset)

with open("dataset_5000.jsonl", "w") as f:
    for entry in dataset:
        f.write(json.dumps(entry) + "\n")

print("✅ 5000-task dataset generated and saved as dataset_5000.jsonl")