import stripe
import os
from fastapi import APIRouter, HTTPException, Request, Security
from fastapi_jwt import JwtAuthorizationCredentials
from pydantic import BaseModel

from app.store.user_repository import access_security
from app.db.database import new_session
from app.db.models import User
from dotenv import load_dotenv

load_dotenv()

stripe_router = APIRouter()

STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
ENDPOINT_SECRET = os.getenv("STRIPE_ENDPOINT_SECRET")
STRIPE_SUCCESS_URL = os.getenv("STRIPE_SUCCESS_URL")
STRIPE_CANCEL_URL = os.getenv("STRIPE_CANCEL_URL")

class CreateCheckoutSessionRequest(BaseModel):
    amount: int
    currency: str

stripe.api_key = STRIPE_API_KEY

def handle_checkout_session(session):
    user_id = session['client_reference_id']
    amount = session['amount_total']
    with new_session() as session:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            user.balance += amount / 100
            session.commit()

@stripe_router.post("/create-checkout-session/")
async def create_checkout_session(
        request: CreateCheckoutSessionRequest,
        credentials: JwtAuthorizationCredentials = Security(access_security)
):
    user_id = credentials.subject.get("id")
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{ 'price_data': {
                'currency': request.currency,
                'product_data': { 'name': 'Your Product Name', },
                'unit_amount': request.amount, },
                'quantity': 1,
            }],
            mode='payment',
            success_url=STRIPE_SUCCESS_URL,
            cancel_url=STRIPE_CANCEL_URL,
            client_reference_id=user_id
        )
        return {"url": session.url}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@stripe_router.post("/webhook/")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, ENDPOINT_SECRET
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        HTTPException(status_code=400, detail="Invalid signature")
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session(session)
        return {"status": "success"}
