import mimetypes
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import tempfile
import uuid

from .stt import transcribe_speech_to_text
from .llm import generate_response
from .tts import transcribe_text_to_speech
from g2p_id import G2P

app = FastAPI(
    title="Voice Chatbot API",
    description="API untuk chatbot berbasis suara dengan integrasi STT, Gemini LLM, dan TTS",
    version="1.0.0",
)


@app.post("/chat")
async def chat_endpoint(audio_file: UploadFile = File(...)):
    """
    Endpoint untuk memproses audio dari pengguna dan mengembalikan respons audio.

    Args:
        audio_file (UploadFile): File audio dalam format WAV

    Returns:
        FileResponse: File audio respons dalam format WAV
    """
    try:
        # Baca file audio yang diunggah
        audio_bytes = await audio_file.read()
        print(f"[DEBUG] Audio file size: {len(audio_bytes)} bytes")

        # Konversi audio ke teks menggunakan Whisper
        user_text = transcribe_speech_to_text(audio_bytes)
        print(f"[DEBUG] Transcribed text: {user_text}")

        if user_text.startswith("[ERROR]"):
            raise HTTPException(status_code=400, detail=user_text)

        # Proses teks menggunakan Gemini LLM
        g2p = G2P()
        response_text_original = generate_response(user_text)
        print(f"[DEBUG] Response from LLM: {response_text_original}")
        response_text = g2p(response_text_original)
        print(f"[DEBUG] Response text after conversion to phonetic: {response_text}")

        if response_text.startswith("[ERROR]"):
            raise HTTPException(status_code=400, detail=response_text)

        # Konversi respons teks ke audio menggunakan Coqui TTS
        response_audio_path = transcribe_text_to_speech(response_text)
        print(f"[DEBUG] Audio file path generated: {response_audio_path}")

        if response_audio_path.startswith("[ERROR]"):
            raise HTTPException(status_code=400, detail=response_audio_path)

        # Validasi MIME type
        mime_type, _ = mimetypes.guess_type(response_audio_path)
        print(f"[DEBUG] MIME type of response audio: {mime_type}")

        # Accept both audio/wav and audio/x-wav
        if mime_type not in ["audio/wav", "audio/x-wav"]:
            raise HTTPException(
                status_code=400,
                detail=f"[ERROR] Output TTS bukan file WAV. MIME type: {mime_type}",
            )

        # 4. Kirim file audio respons
        print(f"[DEBUG] Sending audio file: {response_audio_path}")
        return FileResponse(
            response_audio_path, media_type="audio/wav", filename="response.wav"
        )

    except Exception as e:
        print(f"[ERROR] Exception: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan: {str(e)}")


@app.get("/")
async def root():
    """
    Endpoint untuk mengecek status API
    """
    return {"status": "online", "message": "Voice Chatbot API berjalan dengan baik"}
