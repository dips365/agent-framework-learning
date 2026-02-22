# Speech to Text POC

Real-time complaint capture with a WebSocket audio stream. The backend transcribes audio chunks and streams partial text to the UI. An optional Microsoft Agent Framework cleanup step can fix punctuation and filler words.

## Flow
Mic Start -> Open WebSocket -> Send audio chunks -> Receive transcript text -> Display in "Customer Complaint / Notes"

## Recommended model
- Primary (Azure OpenAI): `gpt-4o-mini-transcribe`
- Alternative: `whisper-1`

Use the **deployment name** you created in Azure OpenAI for the value of `AZURE_OPENAI_TRANSCRIBE_DEPLOYMENT_NAME`.

## Setup
1. Update environment variables in the repo root `.env`:
   - `AZURE_OPENAI_ENDPOINT`
   - `AZURE_OPENAI_API_KEY`
   - `AZURE_OPENAI_API_VERSION`
   - `AZURE_OPENAI_TRANSCRIBE_DEPLOYMENT_NAME`
   - Optional cleanup via Agent Framework:
     - `ENABLE_AGENT_CLEANUP=true`
     - `AZURE_OPENAI_CLEANUP_DEPLOYMENT_NAME` (or reuse `AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME`)

2. Start the server locally:
   ```bash
   python microsoft-agents/speech-to-text/server.py
   ```

3. Open the UI:
   - http://localhost:8001

## Local test endpoint
You can also test transcription without the UI:
```bash
curl -X POST http://localhost:8001/transcribe -F "file=@sample.wav"
```

## Notes
- Audio is sent as 16kHz mono PCM from the browser in short chunks.
- The WebSocket endpoint is `/ws/transcribe`.
- For best results, use a headset mic and speak clearly.
