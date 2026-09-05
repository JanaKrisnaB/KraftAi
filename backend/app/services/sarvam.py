import os
from fastapi import HTTPException
class SarvamService:
 def __init__(self): self.api_key=os.getenv('SARVAM_API_KEY')
 def unavailable(self):
  if not self.api_key: raise HTTPException(503,'Sarvam is not configured. Add SARVAM_API_KEY server-side to enable live speech.')
 def transcribe(self, audio: bytes): self.unavailable(); raise HTTPException(501,'Live Sarvam transcription adapter is not enabled in this local demo.')
 def speak(self,text): self.unavailable(); raise HTTPException(501,'Live Sarvam synthesis adapter is not enabled in this local demo.')
