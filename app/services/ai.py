from fastapi import HTTPException
from openai import OpenAI

from app.core.config import settings


def chat(messages: list[dict]) -> str:
    if not settings.openai_api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    client = OpenAI(api_key=settings.openai_api_key)

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        temperature=0.7,
    )

    return response.choices[0].message.content
