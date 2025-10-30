from typing import Optional, Dict
from pydantic import BaseModel

class Peft_Config(BaseModel):
    model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    model_name_finetuned: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0-HealthCare"

    lora_r: int = 32
    lora_alpha: int = 32
    lora_dropout: float = 0.0

    use_4bit: bool = True
    bnb_4bit_compute_dtype: str = "float16"
    bnb_4bit_quant_type: str = "nf4"
    use_nested_quant: bool = False

    output_dir: str = "./results"

    num_train_epochs: int = 10
    max_steps: int = -1
    warmup_ratio: float = 0.05

    fp16: bool = True
    bf16: bool = False

    per_device_train_batch_size: int = 4
    per_device_eval_batch_size: int = 2
    gradient_accumulation_steps: int = 16

    gradient_checkpointing: bool = True
    max_grad_norm: float = 0.3

    learning_rate: float = 1e-5
    weight_decay: float = 0.001
    optim: str = "paged_adamw_32bit"
    lr_scheduler_type: str = "cosine"

    group_by_length: bool = True
    packing: bool = False
    max_seq_length: Optional[int] = 256

    save_steps: int = 1500
    logging_steps: int = 50

    device_map: Optional[Dict[str, int]] = {"": 0}
