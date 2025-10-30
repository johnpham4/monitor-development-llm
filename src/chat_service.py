from llama_cpp import Llama
from loguru import logger
from typing import Optional
import os

class ChatService:
    def __init__(self):
        self.model_loaded = False
        self.model = None
        self.model_path = "./gguf_model.gguf"
        self.system_prompt = "Bạn là một trợ lý luật pháp Việt Nam thông minh, luôn trả lời bằng tiếng Việt chuẩn và dễ hiểu."

    async def load_model(self):
        try:
            # Check if model exists
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model not found at: {self.model_path}")

            logger.info(f"Loading model from: {self.model_path}")

            # Load model với config tương tự notebook
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=4096,
                n_threads=8,
                verbose=False  # Tắt verbose như notebook
            )
            self.model_loaded = True
            logger.info("LLaMA model loaded successfully")
            return "Loaded successfully"
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise

    def is_model_loaded(self) -> bool:
        return self.model_loaded and self.model is not None

    def generate_response(self, user_input: str, max_tokens: int = 256, temperature: float = 0.7):
        """Batch prediction like in notebook"""
        if not self.model_loaded:
            return "Model not loaded yet."

        # Format như trong notebook - chat template
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_input}
        ]

        generation_options = {
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 0.9,
            "top_k": 40,
            "stop": None,
        }

        try:
            response = self.model.create_chat_completion(messages=messages, **generation_options)
            return response['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Lỗi khi tạo phản hồi: {str(e)}"

    def streaming_response(self, user_input: str, max_tokens: Optional[int] = 256, temperature: Optional[float] = 0.7):
        """Streaming response như trong notebook"""
        if not self.is_model_loaded():
            logger.warn("Model is not loaded")
            yield "Model not loaded yet."
            return

        # Format messages như trong notebook
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_input}
        ]

        generation_options = {
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 0.9,
            "top_k": 40,
            "stop": None,
        }

        try:
            # Streaming như trong notebook
            for chunk in self.model.create_chat_completion(messages=messages, stream=True, **generation_options):
                choice = chunk['choices'][0]['delta']
                if 'content' in choice:
                    yield choice['content']
        except Exception as e:
            logger.error(f"Error in streaming response: {e}")
            yield f"Lỗi khi tạo phản hồi: {str(e)}"

chatService = ChatService()