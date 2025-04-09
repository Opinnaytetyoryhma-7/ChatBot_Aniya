from fastapi import FastAPI
from pydantic import BaseModel
from chat import get_response, log_unknown_input, intents
from backend.database import supabase
import random

app = FastAPI()

class ChatInput(BaseModel):
    message: str

@app.post("/chat")
async def chat(input: ChatInput):
    tag, prob = get_response(input.message)

    if prob > 0.75:
        for intent in intents["intents"]:
            if tag == intent["tag"]:
                response = random.choice(intent['responses'])

                supabase.table("Message").insert({
                    "user_message": input.message,
                    "bot_response": response
                }).execute()

                return {
                    "response": response,
                    "intent": tag,
                    "confidence": round(prob, 2)
                }

    log_unknown_input(input.message)

    return {
        "response": "Pahoittelut, nyt en ymmärtänyt. Haluatko jättää tukipyynnön?",
        "intent": "unknown",
        "confidence": round(prob, 2)
    }