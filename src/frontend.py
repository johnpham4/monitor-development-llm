import gradio as gr
import requests
import json
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

def stream_chat_response(message, history):
    new_history = history + [[message, ""]]
    yield new_history
    try:
        payload = {"message": message, "max_tokens": 256}
        response = requests.post(
            f"{API_BASE_URL}/chat/stream",
            json=payload,
            stream=True,
            timeout=60
        )

        accumulated = ""
        for line in response.iter_lines():
            if line:
                decoded = line.decode("utf-8")
                if decoded.startswith("data: "):
                    data_str = decoded[6:]
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        if "content" in data:
                            accumulated += data["content"]
                        elif "delta" in data and "content" in data["delta"]:
                            accumulated += data["delta"]["content"]

                        new_history[-1][1] = accumulated
                        yield new_history
                    except:
                        continue
    except Exception as e:
        new_history[-1][1] = f"Lỗi: {str(e)}"
        yield new_history

def clear():
    return [], ""


with gr.Blocks(title="Chatbot Luật Việt Nam") as demo:
    gr.Markdown("<h2 style='text-align:center;'>Chatbot Luật Việt Nam</h2>")

    chatbot = gr.Chatbot()

    with gr.Row():
        msg = gr.Textbox(placeholder="Nhập câu hỏi...", show_label=False, scale=8)
        send = gr.Button("Gửi", scale=1)
        clear_btn = gr.Button("Xóa", scale=1)

    def submit(message, history):
        if not message or not message.strip():
            return history, ""
        for update in stream_chat_response(message, history):
            yield update, ""

    send.click(submit, [msg, chatbot], [chatbot, msg])
    msg.submit(submit, [msg, chatbot], [chatbot, msg])
    clear_btn.click(clear, [], [chatbot, msg])

    gr.Markdown("<p style='text-align:center;color:#666;font-size:13px;'>Lưu ý: Chatbot chỉ hỗ trợ tham khảo, không thay thế tư vấn pháp lý.</p>")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
