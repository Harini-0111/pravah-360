"""
PRAVAH 360 - Voice Assistant & Text-To-Speech (TTS) Service
Supports genuine Telugu (te-IN) and Indian English (en-IN) speech synthesis.
Multi-tier pipeline:
1. Google Cloud Text-to-Speech API (te-IN-Standard-A / en-IN-Standard-B) if GOOGLE_TTS_API_KEY is configured.
2. Direct Google Voice TTS audio synthesis (tl=te / tl=en-IN) returning high-quality MP3 audio.
3. Offline browser-side fallback strictly matching te-IN/en-IN locales.
Credentials are kept strictly in backend environment variables.
"""

import os
import base64
import json
import logging
import urllib.request
import urllib.parse
import urllib.error
import re
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class VoiceTtsService:
    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_TTS_API_KEY") or os.environ.get("GOOGLE_CLOUD_API_KEY")
        self.google_cloud_tts_url = "https://texttospeech.googleapis.com/v1/text:synthesize"

    def synthesize_speech(self, text: str, lang: str = "te-IN") -> Dict[str, Any]:
        """
        Synthesize speech for given text in Telugu or English.
        Returns base64 audio if Cloud or Web TTS succeeds, or metadata for client synthesis.
        """
        if not text or not text.strip():
            return {
                "success": False,
                "provider": "none",
                "audio_base64": None,
                "error": "Empty text provided"
            }

        # Normalize language
        is_telugu = lang.startswith("te") or bool(re.search(r"[\u0C00-\u0C7F]", text))
        lang_code = "te-IN" if is_telugu else "en-IN"
        voice_name = "te-IN-Standard-A" if is_telugu else "en-IN-Standard-B"
        tl_code = "te" if is_telugu else "en-IN"

        # Clean text for speech synthesis (remove markdown formatting, bullet symbols, asterisks)
        clean_text = re.sub(r"[*#_~`\[\]()>]", " ", text)
        clean_text = re.sub(r"\s+", " ", clean_text).strip()

        # 1. Tier 1: Google Cloud Text-to-Speech API if API key is present
        if self.api_key:
            try:
                payload = {
                    "input": {"text": clean_text[:600]},
                    "voice": {
                        "languageCode": lang_code,
                        "name": voice_name,
                        "ssmlGender": "FEMALE"
                    },
                    "audioConfig": {
                        "audioEncoding": "MP3",
                        "speakingRate": 0.95,
                        "pitch": 0.0
                    }
                }
                
                req_data = json.dumps(payload).encode("utf-8")
                url = f"{self.google_cloud_tts_url}?key={self.api_key}"
                req = urllib.request.Request(url, data=req_data, headers={"Content-Type": "application/json"})
                
                with urllib.request.urlopen(req, timeout=7) as response:
                    res_body = json.loads(response.read().decode("utf-8"))
                    audio_content = res_body.get("audioContent")
                    if audio_content:
                        return {
                            "success": True,
                            "provider": "google_cloud_tts",
                            "provider_label": "Google Cloud TTS (te-IN-Standard-A)" if is_telugu else "Google Cloud TTS (en-IN-Standard-B)",
                            "lang": lang_code,
                            "voice_name": voice_name,
                            "format": "audio/mp3",
                            "audio_base64": audio_content
                        }
            except Exception as e:
                logger.warning(f"Google Cloud TTS attempt notice: {e}. Trying Google Web TTS fallback.")

        # 2. Tier 2: Direct Google Voice TTS audio synthesis
        try:
            # Take up to first 250 characters for immediate, crisp conversational response
            query_text = clean_text[:240]
            encoded_query = urllib.parse.quote(query_text)
            tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl={tl_code}&client=tw-ob&q={encoded_query}"
            
            req = urllib.request.Request(
                tts_url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            with urllib.request.urlopen(req, timeout=6) as response:
                audio_bytes = response.read()
                if audio_bytes and len(audio_bytes) > 500:
                    b64_audio = base64.b64encode(audio_bytes).decode("utf-8")
                    return {
                        "success": True,
                        "provider": "google_voice_tts",
                        "provider_label": "Google Voice TTS (te-IN)" if is_telugu else "Google Voice TTS (en-IN)",
                        "lang": lang_code,
                        "voice_name": "Google Telugu Voice (te-IN)" if is_telugu else "Google Indian English (en-IN)",
                        "format": "audio/mp3",
                        "audio_base64": b64_audio
                    }
        except Exception as e:
            logger.warning(f"Google Voice TTS network fetch notice: {e}. Falling back to browser speech synthesis.")

        # 3. Tier 3: Browser synthesis fallback (client must select genuine te-IN voice or warn if unavailable)
        return {
            "success": True,
            "provider": "browser_synth_fallback",
            "provider_label": "Browser Speech Synthesis",
            "lang": lang_code,
            "recommended_voice": voice_name,
            "audio_base64": None,
            "text": clean_text,
            "notice": "Cloud TTS unavailable; client browser-side Telugu/English synthesis will be used if installed."
        }

voice_tts_service = VoiceTtsService()
