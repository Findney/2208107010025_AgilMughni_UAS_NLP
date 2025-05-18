import os
import tempfile
import requests
import gradio as gr
import scipy.io.wavfile
from pathlib import Path

# URL API endpoint
API_URL = "http://localhost:8000/chat"

def process_audio(audio_file):
    """
    Fungsi untuk memproses file audio melalui API
    """
    if audio_file is None:
        return None, "Mohon unggah file audio terlebih dahulu"
    
    try:
        # Kirim file audio ke API
        files = {"audio_file": open(audio_file, "rb")}
        response = requests.post(API_URL, files=files)
        
        if response.status_code != 200:
            return None, f"Error: {response.json().get('error', 'Unknown error')}"
            
        # Simpan respons audio ke file temporer
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, "response.wav")
        
        with open(output_path, "wb") as f:
            f.write(response.content)
            
        return output_path, "Berhasil memproses audio!"
        
    except Exception as e:
        return None, f"Terjadi kesalahan: {str(e)}"

# Buat antarmuka Gradio
with gr.Blocks(title="Voice Chatbot") as demo:
    gr.Markdown("""
    # 🎙️ Voice Chatbot
    
    Unggah file audio WAV untuk berbicara dengan chatbot.
    """)
    
    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(
                label="Rekam atau Unggah Audio (format WAV)",
                type="filepath",
                format="wav",
                sources=["upload", "microphone"]
            )
            submit_btn = gr.Button("Kirim", variant="primary")
            
        with gr.Column():
            audio_output = gr.Audio(label="Respons")
            status = gr.Textbox(label="Status")
            
    submit_btn.click(
        fn=process_audio,
        inputs=[audio_input],
        outputs=[audio_output, status]
    )

if __name__ == "__main__":
    demo.launch(share=True)
