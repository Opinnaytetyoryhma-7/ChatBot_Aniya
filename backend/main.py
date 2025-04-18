from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from chat import get_response, intents
from backend.database import save_unknown_message, create_ticket
import random

app = FastAPI()

# TODO: cors


# Määritellään ChatInput-malli, joka määrittelee POST-pyynnössä vastaanotetun datan rakenteen
class ChatInput(BaseModel):
    message: str  # käyttäjän lähettämä viesti
    conversation_state: str | None = None  # keskustelun tila, oletuksena None


class TicketInput(BaseModel):
    issue_description: str  # ongelman kuvaus
    email: EmailStr  # käytetään pydanticin EmailStr-tyyppiä sähköpostiosoitteen kelpoisuuden tarkistamiseen


# Luodaan post-pyyntö, joka vastaanottaa käyttäjän viestin
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

    state = input.conversation_state  # kertoo missä kohtaa keskustelu on menossa
    msg = input.message.strip().lower()

    match state:
        case None:
            return {
                "response": "Pahoittelut, nyt en ymmärtänyt. Haluatko jättää tukipyynnön?",
                "conversation_state": "ask_ticket",
            }

        case "ask_ticket":
            if msg in ["kyllä", "joo", "haluan", "ok", "juu"]:
                return {
                    "response": "Voisitko kuvailla ongelmasi ja jättää yhteystietosi, kiitos!",
                    "conversation_state": "wait_description",
                }
            else:
                return {
                    "response": "Selvä juttu! Hyvää päivänjatkoa!",
                    "conversation_state": "end",
                }

        case "wait_description":
            return {
                "response": "Kiitos! Lisää vielä sähköpostiosoitteesi, niin voimme ottaa sinuun yhteyttä",
                "conversation_state": "wait_email",
                "issue_description": input.message, # tallennetaan esim. React useStateen, lähetetään /ticket-pyynnössä
            }

        case _:
            return {
                "response": "Jokin meni pieleen. Yritetäänpä uudelleen.",
                "conversation_state": None,
            }

# Kun sekä ongelman kuvaus että sähköpostiosoite on saatu, muodostetaan uusi post-pyyntö
@app.post("/ticket")
async def ticket(input: TicketInput):
    create_ticket(input.issue_description, input.email)

    return {
        "response": "Kiitos! Olemme tallentaneet tietosi. Palaamme asiaan heti kun pystymme!"
    }
