from openai import OpenAI
from config import CONFIG

api_key = CONFIG.get('openai', {}).get('api_key')
if api_key is None:
    raise ValueError("OpenAI API key not found in config file.")
model = CONFIG.get('openai', {}).get('model')
if model is None:
    raise ValueError("OpenAI model not found in config file.")

client = OpenAI(api_key=api_key)
def get_embedding(text: str, model=model):
    response = client.embeddings.create(input=text, model=model)
    print(response.usage)
    # 回傳第一筆結果的 embedding
    return response.data[0].embedding