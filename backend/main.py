from fastapi import FastAPI
from pydantic import BaseModel
from chat import get_response, intents
from backend.database import save_unknown_message
import random

app = FastAPI()

# TODO: cors

# Määritellään ChatInput-malli, joka määrittelee POST-pyynnössä vastaanotetun datan rakenteen
class ChatInput(BaseModel):
    message: str # käyttäjän lähettämä viesti

#Luodaan POST-pyyntöjä varten reitti
@app.post("/chat")
async def chat(input: ChatInput):
    tag, prob = get_response(input.message)

    if prob > 0.75:
        for intent in intents["intents"]:
            if tag == intent["tag"]:
                response = random.choice(intent["responses"])

                return {"response": response}

    # Jos botti ei tunnista viestiä, tallennetaan se Supabasen Message-tauluun
    save_unknown_message(input.message)

    # TODO: lisää tukipyynnön tallennus
    return {"response": "Pahoittelut, nyt en ymmärtänyt. Haluatko jättää tukipyynnön?"}
