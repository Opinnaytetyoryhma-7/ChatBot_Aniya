import os
import random
import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from pydantic import BaseModel, EmailStr

# Chatbot & backend functions
import supabase
from chat import get_response, intents, recommend_product
from backend.database import (
    reduce_product_availability,
    save_unknown_message,
    create_ticket,
    create_user,
    get_user_by_email,
    get_products,
    get_tickets,
    create_review,
)
from backend.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    require_admin_user,
    send_email,
)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Get frontend URL from environment variable with localhost as fallback
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI backend"}

# CORS settings
origins = [
    FRONTEND_URL,
    "http://localhost:3000",
    "http://localhost:8000",
    "https://*.railway.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Ticketin updatee frontendissä
class TicketUpdate(BaseModel):
    status: str
    admin_response: Optional[str] = None

# Määritellään ChatInput-malli, joka määrittelee POST-pyynnössä vastaanotetun datan rakenteen
class ChatInput(BaseModel):
    message: str  # käyttäjän lähettämä viesti
    conversation_state: str | None = None  # keskustelun tila, oletuksena None
    issue_description: str | None = None  # ongelman kuvaus, oletuksena None



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

class FeedbackInput(BaseModel):
    clarity: str
    ease_of_use: str
    chatbot_feedback: str
    contact_form_feedback: str

class PurchaseItem(BaseModel):
    name: str
    quantity: int


@app.post("/purchase")
async def purchase_cart_items(items: list[PurchaseItem]):
    try:
        for item in items:
            reduce_product_availability(item.name, item.quantity)
        return {"message": "Purchase completed and inventory updated."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


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
                        response_text = "Here are the best matches: \n" + "\n".join(
                            f"- {product['name']} ({product['price']}€)"
                            for product in products
                        )
                    else:
                        response_text = (
                            "I couldn't find any matching products based on your description."
                        )

                    return {"response": response_text}

                if tag == "recommend":
                    return {
                        "response": random.choice(intent["responses"]),
                        "conversation_state": "wait_recommendation",
                    }
                if tag == "ticket_asking":
                    return {
                        "response": "Could you describe your problem and leave your email, thank you!",
                        "conversation_state": "wait_description",
                    }

                if tag == "goodbye":
                    return {
                        "response": random.choice(intent["responses"]),
                        "conversation_state": "end",
                    }
                response = random.choice(intent["responses"])

                return { "response": response}



    state = input.conversation_state  # kertoo missä kohtaa keskustelu on menossa
    msg = input.message.strip().lower()

    match state:
        case None | "":
            # Jos botti ei tunnista viestiä, tallennetaan se Supabasen Message-tauluun
            save_unknown_message(input.message)
            return {
                "response": "I'm sorry, I don't understand what you mean. Would you like to leave a contact request?",
                "conversation_state": "ask_ticket",
            }

        case "ask_ticket":
            if msg in ["yes", "yeah", "yup", "ok"]:
                return {
                    "response": "Could you describe your problem and leave your email, thank you!",
                    "conversation_state": "wait_description",
                }
            else:
                return {
                    "response": "Got it :) have a nice day!",
                    "conversation_state": "end",
                }

        case "wait_description":
            return {
                "response": "Thank you! Please also leave your email address so we can contact you",
                "conversation_state": "wait_email",
                "issue_description": input.message,  # tallennetaan esim. React useStateen, lähetetään /ticket-pyynnössä
            }

        case "wait_email":
            issue_description = input.issue_description
            email = input.message.strip().lower()

            result = await ticket(TicketInput(
                issue_description=issue_description, email=email
            ))
            return result

        case "wait_recommendation":
            products = recommend_product(input.message)
            if products:
                response_text = "Here are a few recommendations for you: \n" + "\n".join(
                    f"- {product['name']} ({product['price']}€)" for product in products
                )
            else:
                response_text = (
                    "Unfortunately I couldn't find any matching products based on your description."
                )

            return {
                "response": response_text,
                "conversation_state": None,
            }

        case _:
            return {
                "response": "Something went wrong. Please try again.",
                "conversation_state": None,
            }


# Kun sekä ongelman kuvaus että sähköpostiosoite on saatu, muodostetaan uusi post-pyyntö
@app.post("/ticket")
async def ticket(input: TicketInput):
    create_ticket(input.issue_description, input.email)

    return {
        "response": "Thank you! We have saved your information and we'll contact you as soon as possible!",
    }


@app.post("/register", response_model=UserOut)
async def register_user(user: RegisterInput):
    existing_user = get_user_by_email(user.email)
    if existing_user.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
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
            detail="Email or password is incorrect",
        )
    user = res.data[0]
    if not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email or password is incorrect",
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
    status: Optional[str] = Query(None, description="Filter tickets by status"),
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

@app.post("/review")
async def submit_feedback(feedback: FeedbackInput):
    try:
        create_review(
            clarity=feedback.clarity,
            ease_of_use=feedback.ease_of_use,
            chatbot=feedback.chatbot_feedback,
            contact_form=feedback.contact_form_feedback,
        )
        return {"message": "Feedback submitted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/admin/tickets/{ticket_id}", response_model=TicketOutput)
async def update_ticket(
    ticket_id: int,
    update: TicketUpdate,
    current_user: dict = Depends(require_admin_user)
):
    try:
        updated_ticket = (
            supabase.table("tickets")
            .update({
                "status": update.status,
                "admin_response": update.admin_response,
                "updated_at": datetime.now().isoformat()
            })
            .eq("ticket_id", ticket_id)
            .execute()
        ).data[0]
        
        if update.status == "closed" and update.admin_response:
            send_email(
                to_email=updated_ticket["user_email"],
                subject=f"Ticket #{ticket_id} Response",
                body=update.admin_response
            )
            
        return updated_ticket
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/{full_path:path}")
def serve_react_app(full_path: str):
    """
    This ensures React routing works (e.g., /about, /dashboard routes)
    """
    file_path = f"frontend/build/{full_path}"
    if os.path.exists(file_path) and not os.path.isdir(file_path):
        return FileResponse(file_path)
    return FileResponse("frontend/build/index.html")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)