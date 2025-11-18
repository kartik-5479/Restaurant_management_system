from flask import Flask, render_template, request, redirect, url_for
import random, time
from difflib import get_close_matches
from datetime import datetime

app = Flask(__name__)

# Menu dictionary
menu = {
    "Starters": { 
        "Fries": 2.50, "Garlic Bread": 3.50, "Caesar Salad": 9.00, "Chicken Nuggets": 6.75,
        "Grilled Sandwich": 7.50, "Bruschetta": 6.00, "Stuffed Mushrooms": 7.25,
        "Spring Rolls": 5.50, "Onion Rings": 4.50, "Mozzarella Sticks": 6.50,
        "Potato Skins": 7.00, "Pizza": 15.00 
    },
    "Main Course": { 
        "Lunch Meal": 10.50, "Spaghetti Bolognese": 14.00, "Butter Chicken": 15.55,
        "Chicken Shashley": 18.99, "Steak": 20.00, "Fish & Chips": 13.25,
        "Paneer Butter Masala": 12.50, "Mixed Veg Curry": 11.00,
        "Baingan Bharta": 10.50, "Chana Masala": 9.50, "Vegetable Korma": 12.00 
    },
    "Desserts": { 
        "Chocolate Cake": 5.50, "Ice Cream Sundae": 4.50, "French Toast": 6.50,
        "Apple Pie": 5.00, "Cheesecake": 5.75, "Brownie with Ice Cream": 6.25,
        "Creme Brulee": 6.50, "Tiramisu": 6.75, "Lemon Tart": 5.50, "Panna Cotta": 6.00 
    },
    "Breads": { 
        "Tandoori Roti": 1.50, "Butter Naan": 2.00, "Garlic Naan": 2.50, "Plain Naan": 1.75,
        "Cheese Naan": 3.00, "Rumali Roti": 2.00, "Mix Parantha": 2.50,
        "Allu Parantha": 2.50, "Gobhi Parantha": 2.50, "Paneer Parantha": 3.00 
    },
    "Non-Alcoholic Drinks": { 
        "Drinks": 2.00, "Boba Tea": 5.00, "Juice": 3.00, "Coffee": 4.00,
        "Tea": 2.50, "Water": 1.50,"Lemonade": 3.50,"Iced Tea": 3.75,
        "Smoothie - Mango": 5.50,"Smoothie - Strawberry": 5.50,"Hot Chocolate": 4.50
    },
    "Alcoholic Drinks": { 
        "Red Wine Glass": 8.50, "White Wine Glass": 8.50, "Beer (Pint)": 6.00,
        "Cocktail - Mojito": 9.50, "Cocktail - Margarita": 10.00,
        "Whiskey (Single)": 12.00, "Vodka Shot": 7.00, "Gin & Tonic": 9.00,
        "Rum & Coke": 8.50, "Tequila Shot": 7.50, "Jägermeister Bomb": 11.00 
    }
}

# Flatten menu for lookup
flat_menu = {item: price for category in menu.values() for item, price in category.items()}

current_order = []

# AI-enhanced item matching
def find_best_match(query):
    query = query.strip().title()
    if query in flat_menu:
        return query
    matches = get_close_matches(query, flat_menu.keys(), n=1, cutoff=0.5)
    return matches[0] if matches else None

def add_item_to_order(item_name, quantity):
    item_name = find_best_match(item_name)
    if not item_name:
        return False  # AI did not find item

    try:
        qty = int(quantity)
        if qty > 0:
            for item in current_order:
                if item['item'] == item_name:
                    item['quantity'] += qty
                    return True
            current_order.append({"item": item_name, "quantity": qty, "price": flat_menu[item_name]})
            return True
    except:
        return False

def calculate_total_cost():
    total_items = sum(item['quantity']*item['price'] for item in current_order)
    service = total_items * 0.10
    subtotal = total_items + service
    tax = subtotal * 0.15
    total = subtotal + tax
    return {"items_cost": total_items, "service_charge": service, "subtotal": subtotal, "tax": tax, "total": total}

def reset_order():
    current_order.clear()

@app.route('/')
def index():
    return render_template('menu.html', menu=menu, current_order=current_order)

@app.route('/add_item', methods=['POST'])
def add_item():
    name = request.form.get('item_name')
    qty = request.form.get('quantity')
    add_item_to_order(name, qty)
    return redirect(url_for('index'))

@app.route('/generate_receipt')
def generate_receipt_route():
    costs = calculate_total_cost() if current_order else None
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template('receipt.html', current_order=current_order, costs=costs, datetime_now=now)

@app.route('/reset_order')
def reset_order_route():
    reset_order()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
