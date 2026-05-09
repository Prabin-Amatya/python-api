tokenizers
from transformers import pipeline

task_pipeline = pipeline(
    "text-generation",
    model="./flan_t5_habit_model",
    tokenizer="./flan_t5_habit_model"
)

main_task = "Read a book"
result = task_pipeline(
    "Break task into steps: Read a book step by step",
    max_length=128,
    do_sample=True,
    temperature=0.7
)
print("\nGenerated Subtasks:\n", result[0]["generated_text"])