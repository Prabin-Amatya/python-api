
import os
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, Trainer, TrainingArguments

model_name = "google/flan-t5-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

dataset = load_dataset("json", data_files={"train": "dataset_5000.jsonl"}, split="train")

print(f"Dataset size: {len(dataset)}")
print("Sample:", dataset[0])

def preprocess(example):
    inputs = tokenizer(
        example["input"],
        max_length=64,
        truncation=True,
        padding="max_length"
    )

    labels = tokenizer(
        example["output"],
        max_length=128,
        truncation=True,
        padding="max_length"
    )

    labels_ids = [
        (l if l != tokenizer.pad_token_id else -100)
        for l in labels["input_ids"]
    ]

    inputs["labels"] = labels_ids
    return inputs

tokenized_dataset = dataset.map(preprocess)


training_args = TrainingArguments(
    output_dir="./flan_t5_habit_model",
    
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,   
    
    num_train_epochs=3,
    
    save_strategy="steps",
    save_steps=200,                 
    save_total_limit=2,
    
    logging_steps=50,
    
    learning_rate=5e-5,
    fp16=False,
    
    dataloader_num_workers=0,
    
    run_name="flan_t5_cpu_training",
    report_to="none"
)


trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset
)

output_dir = "./flan_t5_habit_model"
checkpoint = None

if os.path.isdir(output_dir):
    checkpoints = [d for d in os.listdir(output_dir) if d.startswith("checkpoint-")]
    
    if len(checkpoints) > 0:
        checkpoints = sorted(checkpoints, key=lambda x: int(x.split("-")[-1]))
        checkpoint = os.path.join(output_dir, checkpoints[-1])
        print(f"🔄 Resuming from checkpoint: {checkpoint}")
    else:
        print("⚠️ No checkpoint found, starting fresh.")
else:
    print("📁 No output directory, starting fresh.")

trainer.train(resume_from_checkpoint=checkpoint)

trainer.save_model("./flan_t5_habit_model")
print("✅ Model saved.")

