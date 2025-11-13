"""
Stripe service for handling subscriptions and payments
"""
import stripe
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import User
from app.utils.config import settings

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_customer(user: User, db: Session) -> str:
    """
    Create a Stripe customer for a user
    Returns the Stripe customer ID
    """
    if user.stripe_customer_id:
        return user.stripe_customer_id
    
    try:
        customer = stripe.Customer.create(
            email=user.email,
            name=user.name,
            metadata={
                "user_id": str(user.id),
                "app_user_id": str(user.id)
            }
        )
        
        user.stripe_customer_id = customer.id
        db.commit()
        
        return customer.id
    except Exception as e:
        print(f"Error creating Stripe customer: {e}")
        raise


def create_checkout_session(user: User, db: Session, success_url: str, cancel_url: str) -> Dict[str, Any]:
    """
    Create a Stripe Checkout session for subscription
    Returns the session URL
    """
    try:
        # Ensure user has a Stripe customer ID
        customer_id = create_stripe_customer(user, db)
        
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': settings.STRIPE_PRICE_ID_MONTHLY,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": str(user.id)
            }
        )
        
        return {
            "session_id": session.id,
            "url": session.url
        }
    except Exception as e:
        print(f"Error creating checkout session: {e}")
        raise


def create_customer_portal_session(user: User, return_url: str) -> Dict[str, Any]:
    """
    Create a Stripe Customer Portal session for managing subscription
    """
    if not user.stripe_customer_id:
        raise ValueError("User does not have a Stripe customer ID")
    
    try:
        session = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id,
            return_url=return_url,
        )
        
        return {
            "url": session.url
        }
    except Exception as e:
        print(f"Error creating customer portal session: {e}")
        raise


def get_subscription_status(user: User) -> Optional[Dict[str, Any]]:
    """
    Get the current subscription status from Stripe
    """
    if not user.stripe_subscription_id:
        return None
    
    try:
        subscription = stripe.Subscription.retrieve(user.stripe_subscription_id)
        return {
            "status": subscription.status,
            "current_period_end": subscription.current_period_end,
            "cancel_at_period_end": subscription.cancel_at_period_end,
        }
    except Exception as e:
        print(f"Error retrieving subscription: {e}")
        return None


def cancel_subscription(user: User) -> Dict[str, Any]:
    """
    Cancel a user's subscription (at period end)
    """
    if not user.stripe_subscription_id:
        raise ValueError("User does not have an active subscription")
    
    try:
        subscription = stripe.Subscription.modify(
            user.stripe_subscription_id,
            cancel_at_period_end=True
        )
        
        return {
            "status": subscription.status,
            "cancel_at_period_end": subscription.cancel_at_period_end,
            "current_period_end": subscription.current_period_end
        }
    except Exception as e:
        print(f"Error canceling subscription: {e}")
        raise


def handle_webhook_event(event: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """
    Handle Stripe webhook events
    """
    event_type = event.get("type")
    data = event.get("data", {}).get("object", {})
    
    try:
        if event_type == "checkout.session.completed":
            # User completed checkout
            session = data
            user_id = int(session.get("metadata", {}).get("user_id"))
            customer_id = session.get("customer")
            subscription_id = session.get("subscription")
            
            user = db.query(User).filter_by(id=user_id).first()
            if user:
                user.stripe_customer_id = customer_id
                user.stripe_subscription_id = subscription_id
                user.is_premium = True
                user.stripe_subscription_status = "active"
                
                # Get subscription details
                subscription = stripe.Subscription.retrieve(subscription_id)
                user.stripe_price_id = subscription.items.data[0].price.id
                user.subscription_start_date = subscription.current_period_start
                user.subscription_end_date = subscription.current_period_end
                
                db.commit()
                return {"success": True, "message": "Subscription activated"}
        
        elif event_type == "customer.subscription.updated":
            # Subscription was updated (e.g., renewed, changed)
            subscription = data
            customer_id = subscription.get("customer")
            
            user = db.query(User).filter_by(stripe_customer_id=customer_id).first()
            if user:
                user.stripe_subscription_status = subscription.get("status")
                user.subscription_end_date = subscription.get("current_period_end")
                user.is_premium = subscription.get("status") == "active"
                db.commit()
                return {"success": True, "message": "Subscription updated"}
        
        elif event_type == "customer.subscription.deleted":
            # Subscription was canceled
            subscription = data
            customer_id = subscription.get("customer")
            
            user = db.query(User).filter_by(stripe_customer_id=customer_id).first()
            if user:
                user.is_premium = False
                user.stripe_subscription_status = "canceled"
                db.commit()
                return {"success": True, "message": "Subscription canceled"}
        
        elif event_type == "invoice.payment_succeeded":
            # Payment succeeded
            invoice = data
            customer_id = invoice.get("customer")
            
            user = db.query(User).filter_by(stripe_customer_id=customer_id).first()
            if user and user.stripe_subscription_id:
                subscription = stripe.Subscription.retrieve(user.stripe_subscription_id)
                user.is_premium = subscription.status == "active"
                user.stripe_subscription_status = subscription.status
                db.commit()
                return {"success": True, "message": "Payment succeeded"}
        
        elif event_type == "invoice.payment_failed":
            # Payment failed
            invoice = data
            customer_id = invoice.get("customer")
            
            user = db.query(User).filter_by(stripe_customer_id=customer_id).first()
            if user:
                user.stripe_subscription_status = "past_due"
                # Don't set is_premium to False immediately - give grace period
                db.commit()
                return {"success": True, "message": "Payment failed"}
        
        return {"success": True, "message": f"Event {event_type} processed"}
    
    except Exception as e:
        print(f"Error handling webhook event {event_type}: {e}")
        return {"success": False, "error": str(e)}

