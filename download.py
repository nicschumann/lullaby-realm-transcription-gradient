
import torch
from faster_whisper import WhisperModel

def model_setup():
    # This file is supposed to download the 2.4GB whisper weights
    # and save them to the image, so that we don't have to do that 
    # when the replica spins up...
    has_cuda = torch.cuda.is_available()
    device = 'cuda' if has_cuda else 'cpu'
    precision = 'float16' if has_cuda else 'int8'
    model_size = 'large-v2'
    _ = WhisperModel(model_size, device=device, compute_type=precision)

if __name__ == "__main__":
    model_setup()