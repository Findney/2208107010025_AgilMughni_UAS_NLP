import os
import tempfile
import requests
import gradio as gr
import scipy.io.wavfile
import base64
from pathlib import Path

# URL API endpoint
API_URL = "http://localhost:8000/chat"


def process_audio(audio_file):
    """
    Fungsi untuk memproses file audio melalui API
    """
    if audio_file is None:
        return None, "Mohon unggah file audio terlebih dahulu", "", ""

    try:
        # Kirim file audio ke API
        files = {"audio_file": open(audio_file, "rb")}
        response = requests.post(API_URL, files=files)

        if response.status_code != 200:
            return (
                None,
                f"Error: {response.json().get('detail', 'Unknown error')}",
                "",
                "",
            )

        # Parse response data
        response_data = response.json()

        # Decode base64 audio and save to temporary file
        audio_bytes = base64.b64decode(response_data["audio"])
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, "response.wav")

        with open(output_path, "wb") as f:
            f.write(audio_bytes)

        return (
            output_path,
            "Berhasil memproses audio!",
            response_data["input_text"],
            response_data["response_text"],
        )

    except Exception as e:
        return None, f"Terjadi kesalahan: {str(e)}", "", ""


# Buat antarmuka Gradio
with gr.Blocks(title="Voice Chatbot", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
    # 🎙️ Voice Chatbot
    
    Unggah file audio WAV atau rekam suara Anda untuk berbicara dengan chatbot.
    """
    )

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 🎤 Input")
            audio_input = gr.Audio(
                label="Rekam atau Unggah Audio",
                type="filepath",
                format="wav",
                sources=["upload", "microphone"],
            )
            input_text = gr.Textbox(
                label="Teks yang Diterjemahkan",
                placeholder="Teks dari audio input akan muncul di sini...",
                lines=3,
            )
            submit_btn = gr.Button("Kirim", variant="primary", size="lg")

        with gr.Column(scale=1):
            gr.Markdown("### 🤖 Respons")
            audio_output = gr.Audio(label="Audio Respons")
            response_text = gr.Textbox(
                label="Teks Respons",
                placeholder="Teks respons akan muncul di sini...",
                lines=3,
            )
            status = gr.Textbox(label="Status", interactive=False)

    submit_btn.click(
        fn=process_audio,
        inputs=[audio_input],
        outputs=[audio_output, status, input_text, response_text],
    )

if __name__ == "__main__":
    demo.launch(share=True)
