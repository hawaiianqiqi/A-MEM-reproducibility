import os
os.environ['HF_ENDPOINT']='https://hf-mirror.com'
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING']='1'
from huggingface_hub import snapshot_download
print('--- miniLM ---', flush=True)
p1=snapshot_download('sentence-transformers/all-MiniLM-L6-v2')
print(p1, flush=True)
print('--- roberta-large ---', flush=True)
p2=snapshot_download('roberta-large', allow_patterns=['*.json','*.txt','*.bin','*.safetensors','*.model','*.spm'])
print(p2, flush=True)
print('HF_DONE', flush=True)
