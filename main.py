from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.cloud import texttospeech
import os
import json
from google.oauth2 import service_account

# Load the service account credentials
credentials = service_account.Credentials.from_service_account_file(
    "path/to/your/service-account-key.json"
)

app = FastAPI(title="AI Crop Doctor Voice API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
google_credentials = os.getenv("GOOGLE_CREDENTIALS")

if google_credentials:
    credentials_info = json.loads(google_credentials)
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info
    )
    client = texttospeech.TextToSpeechClient(credentials=credentials)
else:
    client = texttospeech.TextToSpeechClient()



class SpeakRequest(BaseModel):
    text: str
    language: str = "en-IN"


# Google Cloud language code → voice configuration
VOICE_MAP = {
    "en-IN": "en-IN-Neural2-A",
    "hi-IN": "hi-IN-Neural2-A",
    "mr-IN": "mr-IN-Standard-A",
    "bn-IN": "bn-IN-Standard-A",
    "gu-IN": "gu-IN-Standard-A",
    "ta-IN": "ta-IN-Standard-A",
    "te-IN": "te-IN-Standard-A",
    "kn-IN": "kn-IN-Standard-A",
    "ml-IN": "ml-IN-Standard-A",
    "pa-IN": "pa-IN-Standard-A",
    "or-IN": "or-IN-Standard-A",
    "as-IN": "as-IN-Standard-A",
}


@app.get("/")
def home():
    return {"status": "AI Crop Doctor Voice API is running"}


@app.post("/speak")
def speak(request: SpeakRequest):
    try:
        language = request.language

        voice_name = VOICE_MAP.get(language)

        if not voice_name:
            language = "en-IN"
            voice_name = VOICE_MAP["en-IN"]

        synthesis_input = texttospeech.SynthesisInput(
            text=request.text
        )

        voice = texttospeech.VoiceSelectionParams(
            language_code=language,
            name=voice_name
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        return Response(
            content=response.audio_content,
            media_type="audio/mpeg"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )