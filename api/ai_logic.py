import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / 'configs' / '.env')


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# DB Knowledge for "Training" - Sync with actual DB categories
AVAILABLE_CATEGORIES = ['T-shirts', 'Shirts', 'Dresses', 'Tops', 'Bottom Wear', 'Hoodies', 'Jackets', 'Kurtis', 'Sarees']
SPECIFIC_KEYWORDS = ['jeans', 'kurti', 'kurtis', 'saree', 'sarees', 'pant', 'trousers', 'suit', 'jacket', 't-shirt', 'shirt', 'dress', 'top', 'denim', 'formal', 'casual', 'ethnic']

def parse_user_prompt_rule_based(prompt):
    """
    Expert Rule-Based Agent with flexible gender matching.
    """
    prompt_lower = prompt.lower()
    
    gender = None
    # Flexible gender matching for mens, womens, men's, women's
    if re.search(r'\bwomen\b|\bfemale\b|\bwomens\b', prompt_lower): gender = 'women'
    elif re.search(r'\bmen\b|\bmale\b|\bmens\b', prompt_lower): gender = 'men'

    size = None
    size_match = re.search(r'\b(S|M|L|XL|XXL)\b', prompt, re.I)
    if size_match: size = size_match.group(1).upper()

    price_limit = None
    price_match = re.search(r'(?:under|below|₹|less than|budget|max|limit)\s*(\d+)', prompt, re.I)
    if price_match: price_limit = int(price_match.group(1))

    colors = ['Red', 'Blue', 'Green', 'Black', 'White', 'Grey', 'Yellow', 'Pink', 'Orange']
    found_color = None
    for c in colors:
        if re.search(r'\b' + c + r'\b', prompt, re.I):
            found_color = c
            break

    # Determine Intent
    intent = 'search'
    action = 'list'
    product_reference = None
    product_name_query = None

    if re.search(r'cancel|stop|terminate|remove order|delete order', prompt_lower):
        intent = 'order'
        action = 'cancel'
    elif re.search(r'order|buy|purchase|get|checkout', prompt_lower):
        intent = 'order'
        action = 'checkout'
    elif re.search(r'open|view|click|product \d|the (first|second|third|last|1st|2nd|3rd)', prompt_lower):
        if not re.search(r'show me|search for', prompt_lower):
            intent = 'product_view'
            action = 'open'

    # Filter by specific name keywords
    for sn in SPECIFIC_KEYWORDS:
        if sn in prompt_lower:
            product_name_query = sn
            break

    # Navigation Intent
    if re.search(r'wishlist|saved items|heart', prompt_lower) and intent != 'order':
        if re.search(r'add|save|put', prompt_lower) or re.search(r'to wishlist', prompt_lower):
            intent = 'wishlist'
            action = 'add'
        else:
            intent = 'wishlist'
            action = 'open' if 'open' in prompt_lower or 'show' in prompt_lower or 'view' in prompt_lower else 'list'
    elif re.search(r'cart|basket', prompt_lower) and intent != 'order':
        if re.search(r'add|put|place', prompt_lower) or re.search(r'to cart', prompt_lower):
            intent = 'cart'
            action = 'add'
        else:
            intent = 'cart'
            action = 'open' if 'open' in prompt_lower or 'show' in prompt_lower or 'view' in prompt_lower else 'checkout'
    elif re.search(r'order history|my orders|order list', prompt_lower) or (re.search(r'orders', prompt_lower) and 'open' in prompt_lower):
        intent = 'order'
        action = 'list'
    elif re.search(r'home|back to search|list|results|main page', prompt_lower):
        intent = 'search'
        action = 'list'

    # Strict Category Mapping
    category = None
    if 'dress' in prompt_lower: category = 'Dresses'
    elif 'shirt' in prompt_lower and 't-shirt' not in prompt_lower: category = 'Shirts'
    elif 't-shirt' in prompt_lower: category = 'T-shirts'
    elif 'hoodie' in prompt_lower: category = 'Hoodies'
    elif 'top' in prompt_lower: category = 'Tops'
    elif 'jacket' in prompt_lower: category = 'Jackets'
    elif 'kurti' in prompt_lower: category = 'Kurtis'
    elif 'saree' in prompt_lower: category = 'Sarees'
    elif any(x in prompt_lower for x in ['bottom', 'pant', 'jeans', 'trousers']): category = 'Bottom Wear'

    # Support any number (1st, 2nd, 5th, etc.) or words (first, second, last, fourth, etc.)
    idx_match = re.search(r'\b(first|1st|second|2nd|third|3rd|fourth|4th|fifth|5th|sixth|6th|seventh|7th|eighth|8th|ninth|9th|tenth|10th|last|number \d+|this|that|it)\b', prompt_lower)
    if idx_match: product_reference = idx_match.group(1)

    # Shipping Address Label Extraction
    shipping_address_label = None
    manual_full_address = None
    
    # Check for manual full address first (greedy match after "to" or "at")
    # Improved regex for better extraction
    manual_match = re.search(r'(?:to|at|deliver to|ship to|address:?)\s+([^,.(]*?)(?:\s+(?:using|via|with|payment|via)|$)', prompt_lower)
    if not manual_match:
        manual_match = re.search(r'(?:to|at|deliver to|ship to|address:?)\s+(.*)$', prompt_lower)
    
    if manual_match:
        addr_candidate = manual_match.group(1).strip()
        # If it looks like a short label, it's a label. Otherwise, it's a manual address.
        if len(addr_candidate.split()) <= 2 and addr_candidate.lower() in ['home', 'work', 'office', 'kadapa', 'chennai', 'default', 'mumbai', 'bangalore', 'pune']:
            shipping_address_label = addr_candidate.title()
        else:
            manual_full_address = addr_candidate.title()

    # Fallback label search if not found above
    if not shipping_address_label and not manual_full_address:
        label_match = re.search(r'\b(home|work|office|kadapa|chennai)\b', prompt_lower)
        if label_match: shipping_address_label = label_match.group(1).title()

    # Address Navigation
    address_action = None
    if re.search(r'\baddress\b|\blocation\b|\bship to\b', prompt_lower) and not (shipping_address_label or manual_full_address):
        if re.search(r'edit|change|update|open|show|set', prompt_lower):
            address_action = 'open'

    # Payment Method Detection
    payment_method = 'COD'
    if any(x in prompt_lower for x in ['phonepe', 'google pay', 'paytm', 'upi', 'gpay']):
        payment_method = 'UPI'
    elif any(x in prompt_lower for x in ['card', 'debit', 'credit', 'visa', 'mastercard']):
        payment_method = 'Card'

    # Better Quantity Extraction
    quantity = 1
    qty_num_match = re.search(r'\b(?:qty|quantity|count|get|buy)\s*(\d+)\b', prompt_lower)
    if qty_num_match:
        quantity = int(qty_num_match.group(1))
    else:
        qty_standalone = re.search(r'\b(\d+)\s+(?:items|pieces|copies|units|shirts|tops|jeans|hoodies|jackets)\b', prompt_lower)
        if qty_standalone:
            quantity = int(qty_standalone.group(1))

    # Order ID Extraction (for cancellation)
    order_id = None
    order_id_match = re.search(r'(?:order|#)\s*(\d+)', prompt_lower)
    if order_id_match:
        order_id = int(order_id_match.group(1))

    return {
        "intent": intent,
        "action": action,
        "order_id": order_id,
        "product_reference": product_reference,
        "product_name": product_name_query,
        "category": category,
        "color": found_color,
        "budget": price_limit,
        "gender": gender,
        "size": size,
        "payment_method": payment_method,
        "shipping_address_label": shipping_address_label,
        "manual_full_address": manual_full_address,
        "quantity": quantity,
        "address_action": address_action
    }

def parse_user_prompt_llm(prompt, user_context=None):
    """
    Expert LLM Agent - Handles manual addresses and quantities.
    """
    system_prompt = f"""
    You are the central AI brain of "Fashiopulse AI".
    
    TASK: Parse the user's intent into a JSON object for an autonomous agent.
    
    STRICT JSON SCHEMA:
    {{
      "intent": "search" | "product_view" | "order" | "cart" | "wishlist",
      "action": "list" | "open" | "checkout" | "add" | "cancel",
      "product_name": "string or null",
      "order_id": number or null,
      "product_reference": "first" | "2nd" | "fourth" | "last" | "number 5" | "this" | null,
      "shipping_address_label": "Home" | "Work" | "Kadapa" | null,
      "manual_full_address": "Full string of the address if provided literally (e.g. 'Flat 101, Mumbai')" | null,
      "quantity": number, (EXTRACT ANY NUMBER MENTIONED, e.g. 'Buy 3' -> 3. Default 1)
      "payment_method": "UPI" | "Card" | "COD",
      "address_action": "open" | null
    }}

    ACTION RULES:
    1. If user says "Order", "Buy", "Purchase", "Get it": intent="order", action="checkout".
    2. If user mentions a specific full address (e.g. "Order to Flat 101 Mumbai"), set "manual_full_address". IGNORE saved labels if a full address is present.
    3. If user mentions a label (e.g. "to my Home"), set "shipping_address_label".
    4. If user mentions a quantity (e.g. "Get 3 pairs", "Buy 2", "qty 5"), set "quantity" to that number.
    5. If user mentions payment (UPI, Card, Cash, PhonePe, GPay): set "payment_method".
    6. If user says "Open wishlist" or "My saves": intent="wishlist", action="open".
    7. If user says "Open cart" or "Show basket": intent="cart", action="open".
    8. If user says "Open orders", "Show my orders", or "Order history": intent="order", action="list".
    9. If user says "Add to cart" or "Put in basket" (e.g., "Add 1st item to cart"): intent="cart", action="add", product_reference="1st".
    10. If user says "Add to wishlist" or "Save to wishlist" (e.g., "Add 2nd product to wishlist"): intent="wishlist", action="add", product_reference="2nd".
    11. If user says "Cancel order 123": intent="order", action="cancel", order_id=123.
    
    DATABASE CATEGORIES: {AVAILABLE_CATEGORIES}
    CONTEXT: {user_context}
    
    Return ONLY JSON.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"LLM Reasoning Error: {e}. Falling back to Rule-Based Agent.")
        return parse_user_prompt_rule_based(prompt)
