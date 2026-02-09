from fastapi import APIRouter

router = APIRouter()

TERMS = "Mental Wellness App Terms\n\nUse of this service is subject to respectful and lawful behavior."
POLICY = "Privacy Policy\n\nWe store only the data required to provide the service."
SUPPORT = "Support\n\nEmail support@example.com for help."


@router.get("/terms")
def terms():
    return {"content": TERMS}


@router.get("/policy")
def policy():
    return {"content": POLICY}


@router.get("/support")
def support():
    return {"content": SUPPORT}
