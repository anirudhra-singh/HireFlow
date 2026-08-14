# handles all communication with google gemini api
import httpx
from fastapi import HTTPException, status
from app.core.config import settings


def build_prompt(company_name: str, job_title: str) -> str:
   
    return (
        f"I am applying for the position of '{job_title}' at '{company_name}'. "
        f"Give me 3 short, specific, actionable resume tips to improve my chances. "
        f"Keep the total response under 100 words. "
        f"Format as a numbered list. No introduction, just the tips."
    )


def generate_resume_tip(company_name: str, job_title: str) -> str:
    
    prompt = build_prompt(company_name, job_title)

    #structure of gemini api
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": 200
            }
    }


    url = f"{settings.GEMINI_API_URL}?key={settings.GEMINI_API_KEY}"

    try:
        # if gemini takes more than 15 seconds stop waiting
        response = httpx.post(url, json=payload, timeout=15.0)
        response.raise_for_status()

        data = response.json()

        # extracting the actual text from ai response structure
        tip_text = data["candidates"][0]["content"]["parts"][0]["text"]

        return tip_text.strip()

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="AI service took too long to respond. Please try again."
        )

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="AI usage limit reached. Please try again later."
                )
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI model configuration error. Please contact support."
            )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI service is currently unavailable. Please try again later."
        )

    except (KeyError, IndexError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI service returned an unexpected response."
        )