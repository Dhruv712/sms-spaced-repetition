"""
Subscription routes for Stripe integration
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import User
from app.services.auth import get_current_active_user
from app.services.stripe_service import (
    create_checkout_session,
    create_customer_portal_session,
    get_subscription_status,
    cancel_subscription,
    handle_webhook_event
)
from app.utils.config import settings
from app.services.premium_service import check_sms_limit, check_deck_limit
from app.models import Deck
import stripe
import json

router = APIRouter()


@router.post("/create-checkout-session")
async def create_checkout(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a Stripe Checkout session for subscription
    """
    try:
        # Use FRONTEND_URL from environment, fallback to production URL
        base_url = settings.FRONTEND_URL or "https://trycue.xyz"
        
        success_url = f"{base_url}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{base_url}/subscription/cancel"
        
        result = create_checkout_session(current_user, db, success_url, cancel_url)
        
        return {
            "success": True,
            "session_id": result["session_id"],
            "url": result["url"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating checkout session: {str(e)}")


@router.get("/status")
async def get_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current subscription status
    """
    return {
        "is_premium": current_user.is_premium,
        "stripe_subscription_id": current_user.stripe_subscription_id,
        "stripe_subscription_status": current_user.stripe_subscription_status,
        "subscription_end_date": current_user.subscription_end_date.isoformat() if current_user.subscription_end_date else None
    }


@router.get("/limits")
async def get_limits(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current usage limits and status
    """
    sms_limit = check_sms_limit(current_user, db)
    deck_limit = check_deck_limit(current_user, db)
    
    return {
        "is_premium": current_user.is_premium,
        "sms_reviews": {
            "count": sms_limit["count"],
            "limit": sms_limit["limit"],
            "remaining": sms_limit["remaining"],
            "within_limit": sms_limit["within_limit"]
        },
        "decks": {
            "count": deck_limit["count"],
            "limit": deck_limit["limit"],
            "remaining": deck_limit["remaining"],
            "can_create": deck_limit["can_create"]
        }
    }


@router.get("/debug")
async def debug_subscription_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    Debug endpoint to check subscription status and webhook processing
    """
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "is_premium": current_user.is_premium,
        "stripe_customer_id": current_user.stripe_customer_id,
        "stripe_subscription_id": current_user.stripe_subscription_id,
        "stripe_subscription_status": current_user.stripe_subscription_status,
        "stripe_price_id": current_user.stripe_price_id,
        "subscription_start_date": current_user.subscription_start_date.isoformat() if current_user.subscription_start_date else None,
        "subscription_end_date": current_user.subscription_end_date.isoformat() if current_user.subscription_end_date else None,
    }


@router.post("/portal")
async def create_portal_session(
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a Stripe Customer Portal session for managing subscription
    """
    try:
        base_url = "https://trycue.xyz"
        if settings.ENVIRONMENT == "development":
            base_url = "http://localhost:3000"
        
        return_url = f"{base_url}/profile"
        
        result = create_customer_portal_session(current_user, return_url)
        
        return {
            "success": True,
            "url": result["url"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating portal session: {str(e)}")


@router.post("/cancel")
async def cancel_user_subscription(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cancel user's subscription (at period end)
    """
    try:
        result = cancel_subscription(current_user)
        db.commit()
        
        return {
            "success": True,
            "message": "Subscription will be canceled at the end of the billing period",
            "cancel_at_period_end": result["cancel_at_period_end"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error canceling subscription: {str(e)}")


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhook events
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")
    
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Webhook secret not configured")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        print(f"❌ Webhook payload error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid payload: {str(e)}")
    except stripe.error.SignatureVerificationError as e:
        print(f"❌ Webhook signature verification failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid signature: {str(e)}")
    
    # Handle the event
    print(f"✅ Webhook event received: {event.get('type')}")
    result = handle_webhook_event(event, db)
    print(f"✅ Webhook processed: {result}")
    
    return result


@router.get("/webhook/test")
async def test_webhook_endpoint():
    """
    Simple test endpoint to verify webhook route is accessible
    Returns 200 if endpoint exists (doesn't test signature verification)
    """
    return {
        "status": "ok",
        "message": "Webhook endpoint is accessible. Use POST /subscription/webhook with Stripe signature for real events.",
        "endpoint": "/subscription/webhook",
        "method": "POST"
    }


@router.post("/test-checkout")
async def create_test_checkout(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a test checkout session for testing webhooks
    This will return a checkout URL that you can use to test the payment flow
    """
    try:
        base_url = "https://trycue.xyz"
        if settings.ENVIRONMENT == "development":
            base_url = "http://localhost:3000"
        
        success_url = f"{base_url}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{base_url}/subscription/cancel"
        
        result = create_checkout_session(current_user, db, success_url, cancel_url)
        
        return {
            "success": True,
            "checkout_url": result["url"],
            "session_id": result["session_id"],
            "instructions": {
                "step1": "Click the checkout_url above or copy it to your browser",
                "step2": "Use test card: 4242 4242 4242 4242",
                "step3": "Use any future expiry date (e.g., 12/34)",
                "step4": "Use any 3-digit CVC",
                "step5": "Complete the payment",
                "step6": "Check Railway logs to see if webhook was received",
                "step7": "Check your user's is_premium status in the database"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating test checkout: {str(e)}")

