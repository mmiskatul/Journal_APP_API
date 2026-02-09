import random

from fastapi import APIRouter

router = APIRouter()

AFFIRMATIONS = [
    "I am worthy of care and kindness.",
    "I can handle what comes my way.",
    "Small steps still move me forward.",
    "I choose calm and clarity today.",
    "My feelings are valid and I can work through them.",
]


@router.get("/daily")
def daily_affirmation():
    return {"affirmation": random.choice(AFFIRMATIONS)}
