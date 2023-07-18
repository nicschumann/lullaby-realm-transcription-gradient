import base64
from time import perf_counter

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel
from pydantic import BaseModel
import numpy as np
import torch


class TranscriptionJob(BaseModel):
    bytes: str
    shape: list[int]
    beam_size: int
    language: str # NOTE(Nic): Make this a more precice Enum type
    encoding: str # NOTE(Nic): Make this a more precice Enum type


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

model : WhisperModel = None

# @app.init runs at startup, and loads models into the app's context
@app.on_event("startup")
async def init():
    global model

    # TODO(Nic): set this up to pull from a shared config file
    has_cuda = torch.cuda.is_available()
    device = 'cuda' if has_cuda else 'cpu'
    precision = 'float16' if has_cuda else 'int8'
    model_size = 'large-v2'
    model = WhisperModel(model_size, device=device, compute_type=precision)


# @app.handler runs for every call
@app.post('/')
def handler(data: TranscriptionJob):
    
    # Set start timestamp
    s = perf_counter()
        
    # Decode the request
    string_data = data.bytes
    # shape = data.shape
    beam_size = int(data.beam_size)
    language = data.language
    encoding = data.encoding

    byte_data = string_data.encode(encoding)
    array_data = base64.b64decode(byte_data)
    audio_buffer = np.frombuffer(array_data, dtype=np.float32)

    # Begin transcription    
    segments, _ = model.transcribe(
        audio_buffer,
        beam_size=beam_size,
        language=language,
        vad_filter=False,
        word_timestamps=True
    )

    result = []

    for speech in segments:

        words = list(map(lambda w: {"start": w.start, "end": w.end, "word": w.word, "prob": w.probability}, speech.words))

        segment_result = {
            "speaker": 'User',
            "start": speech.start,
            "end": speech.end,
            "text": speech.text,
            "words": words
        }

        # merge results, if needed...
        if len(result) > 0: # and abs(speech.start - result[-1].end) < 0.05:
            d = speech.words[0].start - result[-1]['words'][-1]['end']
            
            if d < 0.5: # arbitrary threshold
                result[-1]['end'] = speech.end
                result[-1]['text'] += speech.text
                result[-1]['words'] += words

            else:
                result.append(segment_result)

        else:
            result.append(segment_result)

    e = perf_counter()

    response_json = {
        'duration': (e - s),
        'segments': result
    }

    return response_json