from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from backend.database import supabase
from fastapi import Request
from pydantic import BaseModel
from backend.database import update_product_availability
from chat import get_response, intents
from backend.database import (
    save_unknown_message,
    create_ticket,
    create_user,
    get_user_by_email,
    get_products,
    update_product_availability,
)
from fastapi.middleware.cors import CORSMiddleware
import random
from backend.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
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

class ReviewInput(BaseModel):
    clarity: str
    ease_of_use: str
    chatbot_feedback: str
    contact_form_feedback: str

class PurchaseItem(BaseModel):
    name: str
    quantity: int

class ShoppingItem(BaseModel):
    product_id: str
    quantity: int

class ProductUpdateRequest(BaseModel):
    product_name: str
    quantity: int  

# Määritellään ChatInput-malli, joka määrittelee POST-pyynnössä vastaanotetun datan rakenteen
class ChatInput(BaseModel):
    message: str  # käyttäjän lähettämä viesti
    conversation_state: str | None = None  # keskustelun tila, oletuksena None


class TicketInput(BaseModel):
    issue_description: str  # ongelman kuvaus
    email: EmailStr  # käytetään pydanticin EmailStr-tyyppiä sähköpostiosoitteen kelpoisuuden tarkistamiseen


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
                "issue_description": input.message,  # tallennetaan esim. React useStateen, lähetetään /ticket-pyynnössä
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

@app.get("/api/hello")
async def read_root():
    return {"message": "Hello from FastAPI backend!"}

@app.post("/shopping-list")
async def update_shopping_list(
    items: list[ShoppingItem], current_user=Depends(get_current_user)
):
    updated_items = []
    for item in items:
        product = get_products(id=item.product_id).data[0]
        if product["quantity"] < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for {product['name']}"
            )
        
        new_quantity = product["quantity"] - item.quantity
        updated_items.append({"id": item.product_id, "new_quantity": new_quantity})
    
    return {"status": "success", "updated": updated_items}

@app.patch("/products/update")
async def update_product_quantity(update: ProductUpdateRequest):
    # Fetch product by ID
    product = get_products().data
    target = next((p for p in product if p["id"] == update.product_id), None)

    if not target:
        raise HTTPException(status_code=404, detail="Product not found")

    if target["availability"] < update.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")

    new_qty = target["availability"] - update.quantity
    update_product_availability(update.product_id, new_qty)

    return {
        "message": "Product updated",
        "product_name": target["name"],
        "new_quantity": new_qty
    }


from typing import List

class PurchaseItem(BaseModel):
    name: str
    quantity: int

@app.post("/purchase")
async def purchase_cart_items(items: list[PurchaseItem]):
    if not items:
        raise HTTPException(status_code=400, detail="No items provided for purchase.")

    try:
        updates = update_product_availability([item.dict() for item in items])
        print("Purchase updates:", updates)  #Logs
        return {"message": "Purchase completed and inventory updated.", "updates": updates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during purchase: {str(e)}")
    


ADMIN_SECRET_KEY = "your-very-secret-key"  # Need to move to .env in proper form later

@app.get("/admin/tickets")
async def get_all_tickets(request: Request):
    key = request.query_params.get("key")
    if key != ADMIN_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Access denied")

    result = supabase.table("Ticket").select("*").execute()
    return result.data

@app.post("/review")
async def submit_review(input: ReviewInput):
    result = supabase.table("Review").insert({
        "clarity": input.clarity,
        "ease_of_use": input.ease_of_use,
        "chatbot_feedback": input.chatbot_feedback,
        "contact_form_feedback": input.contact_form_feedback,
    }).execute()

    if result.error:
        raise HTTPException(status_code=500, detail="Failed to submit review")

    return {"message": "Arvostelu vastaanotettu! Kiitos palautteestasi."}