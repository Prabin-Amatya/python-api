
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import json
import torch

model_name = "google/flan-t5-base"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def generate_subtasks(main_task, max_subtasks=7):
    prompt = f"""
    Break down this task into small physical actions a human would perform.

    Even if the task is simple,
    expand it into smaller actions that takes place before that action.
    Suggest whatever can be completed within 1 minute. And then suggest bigger tasks

    Task: {main_task}

    Steps:
    1.
    """

    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    outputs = model.generate(
        inputs["input_ids"],
        max_length=200,

        # FORCE diversity
        do_sample=True,
        temperature=1.0,
        top_k=50,
        top_p=0.9,

        repetition_penalty=1.3,

        # 🔥 generate MULTIPLE outputs
        num_return_sequences=3
    )

    all_texts = []
    for i, output in enumerate(outputs):
        text = tokenizer.decode(output, skip_special_tokens=True)
        print(f"\nOUTPUT {i+1}:\n{text}\n")
        all_texts.append(text)

    # pick the longest output (usually best)
    text = max(all_texts, key=len)

    # Parse
    subtasks = []
    for line in text.split("\n"):
        line = line.strip()

        if not line:
            continue

        if "." in line:
            parts = line.split(".", 1)
            if parts[0].isdigit():
                line = parts[1].strip()

        if main_task.lower() in line.lower():
            continue

        subtasks.append({
            "name": line,
            "status": "pending"
        })

    # fallback
    if len(subtasks) == 0:
        subtasks = [
            {"name": "Plan the task", "status": "pending"},
            {"name": "Gather materials", "status": "pending"},
            {"name": "Start execution", "status": "pending"},
            {"name": "Track progress", "status": "pending"},
            {"name": "Fix issues", "status": "pending"},
            {"name": "Finalize", "status": "pending"},
            {"name": "Review", "status": "pending"},
        ]

    return {
        "main_task": main_task,
        "sub_tasks": subtasks[:max_subtasks]
    }

if __name__ == "__main__":

    while True:
        user_input = input("\nEnter a task (or type 'exit'): ")

        if user_input.lower() == "exit":
            break

        result = generate_subtasks(user_input)

        print("\nFINAL JSON OUTPUT:\n")
        print(json.dumps(result, indent=4))