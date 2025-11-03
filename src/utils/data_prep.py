from datasets import load_dataset, Dataset
from tqdm.auto import tqdm
import pandas as pd
from sklearn.model_selection import train_test_split

def preprocess_function(example):
    SYSTEM_PROMPT = (
    "Bạn là một trợ lý luật pháp Việt Nam thông minh, luôn trả lời bằng tiếng Việt chuẩn và dễ hiểu."
    )
    user_content = example["question"].strip()
    assistant_content = example["answer"].strip()

    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": assistant_content}
        ]
    }

def get_dataset(n_samples=8000):
    ds = load_dataset("thangvip/vietnamese-legal-qa", split="train")

    rows = []

    for i in tqdm(range(len(ds))):
        qa_pairs = ds[i]["generated_qa_pairs"]
        for qa_pair in qa_pairs:
            rows.append({
                "question": qa_pair["question"],
                "answer": qa_pair["answer"]
            })

    df = pd.DataFrame(rows)

    df = df.assign(
        num_tokens=df["answer"].apply(lambda text: len(str(text).split()))
    )

    df = df.loc[df["num_tokens"] < 256]
    if len(df) > n_samples:
        df = df.sample(n_samples, random_state=42).reset_index(drop=True)

    # df_train, df_val = train_test_split(df, test_size=0.1, random_state=42)

    ds_train = Dataset.from_pandas(df)
    # ds_val = Dataset.from_pandas(df_val)

    # Áp dụng preprocess_function
    ds_train = ds_train.map(preprocess_function).select_columns(["messages"])
    # ds_val = ds_val.map(preprocess_function).select_columns(["messages"])

    return ds_train

def tokenize_and_mask(example, tokenizer, max_length):
    messages = example["messages"]
    prompt_messages = messages[:-1]
    completion = messages[-1]["content"] + tokenizer.eos_token

    prompt_text = tokenizer.apply_chat_template(prompt_messages, tokenize=False, add_generation_prompt=False)
    full_text = prompt_text + completion

    tokenized_full = tokenizer(full_text, truncation=True, max_length=max_length, padding="max_length")
    tokenized_prompt = tokenizer(prompt_text, truncation=True, max_length=max_length)

    prompt_len = len(tokenized_prompt["input_ids"])
    input_ids = tokenized_full["input_ids"]
    attention_mask = tokenized_full.get("attention_mask", [1]*len(input_ids))

    labels = [-100] * prompt_len + input_ids[prompt_len:]
    labels = labels + [-100] * (max_length - len(labels))
    labels = labels[:max_length]

    return {"input_ids": input_ids, "attention_mask": attention_mask, "labels": labels}
