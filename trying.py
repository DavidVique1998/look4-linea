import io
import base64
from PIL import Image
from openai import OpenAI  

openai = OpenAI()  # Inicializar cliente OpenAI
response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": [
        {
            "type": "text",
            "text": "Puedes describirme esta imagen?"
        },
        {
    "type": "file",
    "file": {
        "url": "https://s3.eu-central-1.wasabisys.com/in-files/593999858262/document.pdf",
        "format": "pdf"
    }},
        ],
        },
    ],
)
classification = response.choices[0].message.content
print("Resultado de clasificación:", classification)