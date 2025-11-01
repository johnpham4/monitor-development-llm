import gradio as gr
import requests
import json
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/v1")

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

    # Examples
    gr.Markdown("### 💡 Câu hỏi mẫu:")

    examples = [
        "Theo Điều 161 Dự thảo Luật Kinh doanh bảo hiểm (sửa đổi), cơ quan quản lý nhà nước về hoạt động kinh doanh bảo hiểm hoạt động trên những nguyên tắc nào?",
        "Dựa vào Điều 59 của Luật Hàng không dân dụng Việt Nam, chức năng chính của Cảng vụ hàng không là gì?",
        "Một công dân Việt Nam sinh con ở nước ngoài và muốn nộp hồ sơ hưởng chế độ thai sản tại Việt Nam. Theo Điều 61 của Luật Bảo hiểm xã hội, giấy tờ này cần đáp ứng những yêu cầu gì?",
        "Theo Điều 8 của Luật Thi hành án dân sự, người phiên dịch có những trách nhiệm gì và phải chịu trách nhiệm như thế nào nếu cố ý dịch sai?",
        "Điều 37 của Dự thảo Luật Giao thông đường bộ (sửa đổi) quy định gì về việc thi công xây dựng, sửa chữa đường bộ ở nơi giao nhau đồng mức với đường sắt?"
    ]

    def set_example_question(example_text):
        return example_text, []

    # Hiển thị theo 2 cột
    with gr.Row():
        with gr.Column():
            for i, example in enumerate(examples):
                if i % 2 == 0:  # cột 1
                    short_text = example[:80] + "..." if len(example) > 80 else example
                    example_btn = gr.Button(f"📋 {short_text}")
                    example_btn.click(
                        fn=set_example_question,
                        inputs=[gr.State(example)],
                        outputs=[msg, chatbot]
                    )
        with gr.Column():
            for i, example in enumerate(examples):
                if i % 2 != 0:  # cột 2
                    short_text = example[:80] + "..." if len(example) > 80 else example
                    example_btn = gr.Button(f"📋 {short_text}")
                    example_btn.click(
                        fn=set_example_question,
                        inputs=[gr.State(example)],
                        outputs=[msg, chatbot]
                    )

    gr.Markdown("<p style='text-align:center;color:#666;font-size:13px;'>Lưu ý: Chatbot chỉ hỗ trợ tham khảo, không thay thế tư vấn pháp lý.</p>")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
