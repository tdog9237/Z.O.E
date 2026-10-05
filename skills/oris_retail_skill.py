"""
Project ORIS (Online Retail Informational System) Skill for Z.O.E.
===================================================================
Aligned with Pearson BTEC Unit 04 Programming: Project ORIS scenario.
Provides automated FAQ resolution, order tracking, returns guidance,
and product stock queries for an online retail business.
"""

import re
from typing import Dict, Any, Optional
from .base_skill import BaseSkill

# Simulated Retail Database for Project ORIS
_ORIS_ORDERS = {
    "ORIS-1001": {"status": "Delivered", "item": "Ergonomic Mechanical Keyboard", "carrier": "Royal Mail", "eta": "Delivered on Friday"},
    "ORIS-1002": {"status": "In Transit", "item": "Noise-Cancelling Bluetooth Headphones", "carrier": "DPD", "eta": "Tomorrow by 2:00 PM"},
    "ORIS-1003": {"status": "Processing", "item": "4K Ultra-HD 27-inch Monitor", "carrier": "DHL Express", "eta": "Dispatched in 24 hours"},
    "ORIS-1042": {"status": "Out for Delivery", "item": "Wireless Optical Gaming Mouse", "carrier": "Amazon Logistics", "eta": "Today by 6:00 PM"},
}

_ORIS_INVENTORY = {
    "keyboard": {"name": "ORIS Pro Mechanical Keyboard", "price": 49.99, "stock": 14},
    "mouse": {"name": "ORIS Precision Wireless Mouse", "price": 24.99, "stock": 28},
    "headphones": {"name": "ORIS Studio ANC Headphones", "price": 79.99, "stock": 5},
    "monitor": {"name": "ORIS 27-inch 4K IPS Monitor", "price": 229.99, "stock": 0},
    "webcam": {"name": "ORIS StreamCam 1080p 60FPS", "price": 39.99, "stock": 9},
}


class OrisRetailSkill(BaseSkill):
    name = "Project ORIS Retail Assistant"
    description = "Answers retail FAQs, looks up order delivery statuses, explains return policies, and checks product stock."
    triggers = [
        "oris", "order", "track", "delivery", "shipping",
        "return policy", "refund", "returns", "exchange",
        "opening hours", "store hours", "customer service",
        "stock", "in stock", "product price", "buy"
    ]
    author = "Pearson BTEC Curriculum / Z.O.E Team"
    version = "1.0.0"

    def can_handle(self, message: str) -> bool:
        msg = message.lower().strip()
        
        # Explicit ORIS mention
        if "oris" in msg:
            return True
            
        # Order tracking (e.g. "where is my order", "track ORIS-1002", "order status")
        if any(w in msg for w in ["track", "order status", "delivery status", "where is my order"]) or \
           re.search(r'\boris-\d{4}\b', msg):
            return True
            
        # Return and refund inquiries
        if any(term in msg for term in ["return policy", "how do i return", "can i get a refund", "refund policy", "exchange item"]):
            return True
            
        # Store hours / contact
        if any(term in msg for term in ["opening hours", "store hours", "when are you open", "contact support"]):
            return True
            
        # Stock queries
        if ("stock" in msg or "price" in msg or "do you sell" in msg or "available" in msg) and \
           any(p in msg for p in _ORIS_INVENTORY.keys()):
            return True

        return False

    def execute(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        msg = message.lower().strip()

        # 1. Order Tracking Lookup
        order_match = re.search(r'\boris-(\d{4})\b', msg)
        if order_match or ("order" in msg and any(ch.isdigit() for ch in msg)):
            order_id = f"ORIS-{order_match.group(1)}" if order_match else None
            if not order_id:
                # Find any 4-digit number
                num_match = re.search(r'\b(\d{4})\b', msg)
                if num_match:
                    order_id = f"ORIS-{num_match.group(1)}"

            if order_id and order_id in _ORIS_ORDERS:
                order = _ORIS_ORDERS[order_id]
                return (
                    f"Order {order_id} for '{order['item']}' is currently {order['status']}. "
                    f"Courier: {order['carrier']}. Estimated arrival: {order['eta']}."
                )
            elif order_id:
                return f"I couldn't locate order reference '{order_id}'. Please verify the 4-digit order number (e.g. ORIS-1001, ORIS-1002, or ORIS-1042)."
            else:
                return "To track your delivery, please provide your 4-digit ORIS order number (for example: ORIS-1001 or ORIS-1042)."

        # 2. Return & Refund Policy
        if any(term in msg for term in ["return", "refund", "exchange"]):
            return (
                "Project ORIS offers a 30-day no-hassle return policy! "
                "Items must be in their original packaging and undamaged condition. "
                "Once returned, refunds are processed back to your original payment method within 3 to 5 business days."
            )

        # 3. Store Hours & Customer Support
        if any(term in msg for term in ["hour", "open", "time", "contact", "support"]):
            return (
                "Project ORIS customer support is available Monday through Friday from 8:30 AM to 6:00 PM, "
                "and Saturdays from 9:00 AM to 1:00 PM. We are closed on Sundays. "
                "You can also email support at support@oris-retail.example.com."
            )

        # 4. Product Stock & Pricing
        for prod_key, prod_info in _ORIS_INVENTORY.items():
            if prod_key in msg:
                if prod_info["stock"] > 0:
                    return (
                        f"Yes! The {prod_info['name']} is currently in stock with {prod_info['stock']} units available "
                        f"at £{prod_info['price']:.2f}. Would you like help with ordering?"
                    )
                else:
                    return (
                        f"The {prod_info['name']} is currently out of stock at £{prod_info['price']:.2f}. "
                        "New inventory is expected to arrive within 7 business days."
                    )

        # 5. General ORIS Overview
        return (
            "Welcome to Project ORIS (Online Retail Informational System)! "
            "I can assist you with tracking orders, checking product stock, "
            "explaining return policies, or store opening hours. How can I help you today?"
        )
