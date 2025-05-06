from fastapi import FastAPI, HTTPException, Depends, status, Query
from typing import Optional, List
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from chat import get_response, intents, recommend_product
from backend.database import (
    save_unknown_message,
    create_ticket,
    create_user,
    get_user_by_email,
    get_products,
    get_tickets,
)
from fastapi.middleware.cors import CORSMiddleware
import random
from backend.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    require_admin_user,
)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# cors
origins = [
    "http://localhost:3000",  # React-frontend, muuta tarvittaessa
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # sallii vain määritellyt osoitteet
    allow_credentials=True,  # esim. JWT-tokenit
    allow_methods=["*"],  # sallii kaikki HTTP-metodit
    allow_headers=["*"],  # sallii kaikki headerit
)


# Määritellään ChatInput-malli, joka määrittelee POST-pyynnössä vastaanotetun datan rakenteen
class ChatInput(BaseModel):
    message: str  # käyttäjän lähettämä viesti
    conversation_state: str | None = None  # keskustelun tila, oletuksena None


class TicketInput(BaseModel):
    issue_description: str  # ongelman kuvaus
    email: EmailStr  # käytetään pydanticin EmailStr-tyyppiä sähköpostiosoitteen kelpoisuuden tarkistamiseen
    user_id: Optional[str] = None  # käyttäjätunnus, oletuksena None


class TicketOutput(BaseModel):
    ticket_id: int
    user_id: Optional[str]
    issue_description: str
    status: str
    user_email: EmailStr
    created_at: str


class RegisterInput(BaseModel):
    email: EmailStr
    password: str
    fname: str
    lname: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):  # vältetäään palauttamasta salasanaa frontendille
    id: str
    email: EmailStr


# Luodaan post-pyyntö, joka vastaanottaa käyttäjän viestin
@app.post("/chat")
async def chat(input: ChatInput):
    tag, prob = get_response(input.message)

    if prob > 0.75:
        for intent in intents["intents"]:
            if tag == intent["tag"]:
                if tag == "recommend_product":
                    products = recommend_product(input.message)
                    if products:
                        response_text = "Tässä parhaat ehdotukset: \n" + "\n".join(
                            f"- {product['name']} ({product['price']}€)"
                            for product in products
                        )
                    else:
                        response_text = (
                            "En löytänyt sopivaa tuotetta annetuilla hakuehdoilla."
                        )

                    return {"response": response_text}

                if tag == "recommend":
                    return {
                        "response": random.choice(intent["responses"]),
                        "conversation_state": "wait_recommendation",
                    }

                if tag == "goodbye":
                    return {
                        "response": random.choice(intent["responses"]),
                        "conversation_state": "end",
                    }
                response = random.choice(intent["responses"])

                return { "response": response}

    # Jos botti ei tunnista viestiä, tallennetaan se Supabasen Message-tauluun
    save_unknown_message(input.message)

    state = input.conversation_state  # kertoo missä kohtaa keskustelu on menossa
    msg = input.message.strip().lower()

    match state:
        case None | "":
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
                "issue_description": input.message,  # tallennetaan esim. React useStateen, lähetetään /ticket-pyynnössä
            }

        case "wait_recommendation":
            products = recommend_product(input.message)
            if products:
                response_text = "Tässä muutama vaihtoehto sinulle: \n" + "\n".join(
                    f"- {product['name']} ({product['price']}€)" for product in products
                )
            else:
                response_text = (
                    "Valitettavasti en löytänyt sopivaa tuotetta kuvauksen perusteella."
                )

            return {
                "response": response_text,
                "conversation_state": None,
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


@app.post("/register", response_model=UserOut)
async def register_user(user: RegisterInput):
    existing_user = get_user_by_email(user.email)
    if existing_user.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Käyttäjä on jo olemassa"
        )

    hashed_pw = hash_password(user.password)
    new_user = (
        create_user(
            fname=user.fname,
            lname=user.lname,
            email=user.email,
            password=hashed_pw,
        )
        .execute()
        .data[0]
    )

    return {"id": new_user["user_id"], "email": new_user["email"]}


@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    res = get_user_by_email(form_data.username)
    if not res.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Käyttäjätunnus tai salasana virheellinen",
        )
    user = res.data[0]
    if not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Käyttäjätunnus tai salasana virheellinen",
        )

    token = create_access_token({"sub": str(user["user_id"])})

    return Token(
        access_token=token, token_type="bearer"
    )  # frontendille lähetettävä token


@app.get("/users/me", response_model=UserOut)  # palauttaa kirjautuneen käyttäjän tiedot
async def read_users_me(current_user=Depends(get_current_user)):
    return {"id": current_user["user_id"], "email": current_user["email"]}


@app.get("/products")
async def get_products_list():
    products = get_products()
    return products.data

@app.get("/admin/tickets", response_model=List[TicketOutput])
async def get_tickets_list(
    status: Optional[str] = Query(None, description="Suodata tiketit statuksen mukaan"),
    current_user: dict = Depends(require_admin_user),
):
    try:
        tickets = get_tickets()
        if status:
            tickets = tickets.eq("status", status)

        tickets = tickets.order("created_at", desc=True)

        response = tickets.execute()

        return response.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
