from __future__ import annotations

import asyncio
import io
import os
import wave
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import AzureOpenAI

from agent_framework import Agent
from agent_framework.azure import AzureOpenAIResponsesClient

load_dotenv(override=True)

APP_DIR = Path(__file__).parent
STATIC_DIR = APP_DIR / "static"

AUDIO_SAMPLE_RATE = int(os.getenv("AUDIO_SAMPLE_RATE", "16000"))
AUDIO_CHUNK_SECONDS = float(os.getenv("AUDIO_CHUNK_SECONDS", "2"))
AUDIO_CHANNELS = 1
AUDIO_SAMPLE_WIDTH = 2

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_TRANSCRIBE_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_TRANSCRIBE_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview")
AZURE_OPENAI_TRANSCRIBE_DEPLOYMENT_NAME = os.getenv(
    "AZURE_OPENAI_TRANSCRIBE_DEPLOYMENT_NAME", "gpt-4o-mini-transcribe"
)

ENABLE_AGENT_CLEANUP = os.getenv("ENABLE_AGENT_CLEANUP", "false").lower() == "true"
CLEANUP_MIN_CHARS = int(os.getenv("CLEANUP_MIN_CHARS", "24"))
AZURE_OPENAI_CLEANUP_DEPLOYMENT_NAME = (
    os.getenv("AZURE_OPENAI_CLEANUP_DEPLOYMENT_NAME")
    or os.getenv("AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME")
    or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
)

app = FastAPI(title="Speech to Text POC", version="0.1.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def _create_transcription_client() -> AzureOpenAI:
    if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_API_KEY:
        raise RuntimeError(
            "Missing Azure OpenAI settings. Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY."
        )
    return AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version=AZURE_OPENAI_API_VERSION,
    )


def _build_wav_buffer_from_pcm16(pcm_audio_bytes: bytes, sample_rate: int) -> io.BytesIO:
    wav_audio_buffer = io.BytesIO()
    with wave.open(wav_audio_buffer, "wb") as wav_file:
        wav_file.setnchannels(AUDIO_CHANNELS)
        wav_file.setsampwidth(AUDIO_SAMPLE_WIDTH)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_audio_bytes)
    wav_audio_buffer.seek(0)
    wav_audio_buffer.name = "audio.wav"
    return wav_audio_buffer


def _transcribe_pcm_chunk(pcm_audio_bytes: bytes) -> str:
    transcription_client = _create_transcription_client()
    wav_audio_buffer = _build_wav_buffer_from_pcm16(pcm_audio_bytes, AUDIO_SAMPLE_RATE)
    transcription_result = transcription_client.audio.transcriptions.create(
        model=AZURE_OPENAI_TRANSCRIBE_DEPLOYMENT_NAME,
        file=wav_audio_buffer,
    )
    return (getattr(transcription_result, "text", None) or "").strip()


def _transcribe_uploaded_file(file_bytes: bytes, filename: str) -> str:
    transcription_client = _create_transcription_client()
    file_buffer = io.BytesIO(file_bytes)
    file_buffer.name = filename or "upload.wav"
    transcription_result = transcription_client.audio.transcriptions.create(
        model=AZURE_OPENAI_TRANSCRIBE_DEPLOYMENT_NAME,
        file=file_buffer,
    )
    return (getattr(transcription_result, "text", None) or "").strip()


async def _cleanup_transcript_if_enabled(raw_transcript: str) -> str:
    if not ENABLE_AGENT_CLEANUP:
        return raw_transcript
    if not AZURE_OPENAI_CLEANUP_DEPLOYMENT_NAME:
        return raw_transcript
    if len(raw_transcript.strip()) < CLEANUP_MIN_CHARS:
        return raw_transcript

    instructions = (
        "You clean up speech transcripts for car service complaints. "
        "Fix punctuation, remove filler words, and keep the original meaning. "
        "Do not add any new details. Return only the cleaned text."
    )

    async with Agent(
        client=AzureOpenAIResponsesClient(
            endpoint=AZURE_OPENAI_ENDPOINT,
            deployment_name=AZURE_OPENAI_CLEANUP_DEPLOYMENT_NAME,
            api_version=AZURE_OPENAI_API_VERSION,
            api_key=AZURE_OPENAI_API_KEY,
        ),
        name="ComplaintCleanup",
        instructions=instructions,
    ) as cleanup_agent:
        cleanup_result = await cleanup_agent.run(raw_transcript)

    return (getattr(cleanup_result, "text", None) or str(cleanup_result)).strip()


@app.get("/")
async def root() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/transcribe")
async def transcribe_file(file: UploadFile = File(...)) -> dict[str, str]:
    uploaded_file_bytes = await file.read()
    transcribed_text = await asyncio.to_thread(
        _transcribe_uploaded_file,
        uploaded_file_bytes,
        file.filename or "upload.wav",
    )
    cleaned_text = await _cleanup_transcript_if_enabled(transcribed_text)
    return {"text": cleaned_text}


@app.websocket("/ws/transcribe")
async def ws_transcribe(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_json({"type": "ready"})

    audio_buffer = bytearray()
    bytes_per_chunk_window = int(AUDIO_SAMPLE_RATE * AUDIO_SAMPLE_WIDTH * AUDIO_CHUNK_SECONDS)

    try:
        while True:
            incoming_message = await websocket.receive()
            if incoming_message.get("bytes"):
                audio_buffer.extend(incoming_message["bytes"])

                while len(audio_buffer) >= bytes_per_chunk_window:
                    audio_chunk = bytes(audio_buffer[:bytes_per_chunk_window])
                    del audio_buffer[:bytes_per_chunk_window]

                    transcribed_text = await asyncio.to_thread(_transcribe_pcm_chunk, audio_chunk)
                    if transcribed_text:
                        cleaned_text = await _cleanup_transcript_if_enabled(transcribed_text)
                        await websocket.send_json({"type": "partial", "text": cleaned_text})
            elif incoming_message.get("text"):
                if incoming_message["text"] == "__flush__" and audio_buffer:
                    audio_chunk = bytes(audio_buffer)
                    audio_buffer.clear()
                    transcribed_text = await asyncio.to_thread(_transcribe_pcm_chunk, audio_chunk)
                    if transcribed_text:
                        cleaned_text = await _cleanup_transcript_if_enabled(transcribed_text)
                        await websocket.send_json({"type": "final", "text": cleaned_text})
    except WebSocketDisconnect:
        return
    except Exception as error:
        await websocket.send_json({"type": "error", "message": str(error)})
        await websocket.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8001, reload=True)
