from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# Allow browser requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://localhost:11434/api/generate"

SYSTEM_PROMPT = """
You are Mitra, a trusted farming assistant for Indian farmers.

Your job:
- Help farmers with crop care, soil, irrigation, pests, diseases, and weather-related issues
- Give practical advice that farmers can actually follow in the field

Rules you MUST follow:
- Answer in **4 to 6 clear points**, written as short paragraphs
- Use **very simple, everyday words**
- Avoid scientific or technical terms
- Do NOT write long explanations
- Be practical, step-by-step, and focused on action
- Do NOT guarantee crop yield or results
- If you are not fully sure, clearly say:
  “Please consult your local agriculture officer”

Tone & style:
- Friendly and respectful
- Calm and reassuring
- Supportive, like a helpful village guide
- Easy to understand for farmers

Important:
- Adapt advice to Indian farming conditions
- Keep answers helpful but not too long
- End every answer politely with a caring closing line

"""

# ---------- Weather helper ----------
def get_weather():
    try:
        # Example location (South India). Can be changed later.
        url = (
            "https://api.open-meteo.com/v1/forecast"
            "?latitude=13.0&longitude=80.0&current_weather=true"
        )
        data = requests.get(url, timeout=5).json()
        temp = data["current_weather"]["temperature"]
        return f"Current temperature is {temp}°C. Consider this while giving advice."
    except:
        return ""


@app.get("/")
def root():
    return {"status": "KrushiMitra backend running"}


@app.post("/chat")
def chat(prompt: str, lang: str = "en"):
    # Language instructions
    language_map = {
        "en": "Reply in simple English.",
        "ta": "Reply in simple Tamil language.",
        "ml": "Reply in simple Malayalam language."
    }

    weather_info = get_weather()

    final_prompt = (
        SYSTEM_PROMPT
        + "\n"
        + weather_info
        + "\n"
        + language_map.get(lang, "Reply in simple English.")
        + "\nAnswer only in bullet points."
        + "\nFarmer question: "
        + prompt
        + "\nAnswer:"
    )

    payload = {
        "model": "gemma3:4b",
        "prompt": final_prompt,
        "stream": False,
    }

    try:
        res = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120
        )

        res.raise_for_status()
        data = res.json()

        return {"response": data.get("response", "No response from AI.")}

    except Exception as e:
        print("OLLAMA ERROR:", e)
        return {"response": "AI service is not available right now. Please try again."}
