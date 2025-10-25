

import requests
import random
import time

API_URL = "http://localhost:8000/products/"

ADJECTIVES = ["Vibrant", "Classic", "Elegant", "Rustic", "Sunshine", "Midnight", "Enchanted", "Jubilant", "Serene", "Blushing", "Golden", "Winter"]
FLOWER_NAMES = ["Rose", "Lily", "Tulip", "Orchid", "Daisy", "Sunflower", "Peony", "Hydrangea", "Carnation", "Freesia", "Lavender", "Marigold"]
PRODUCT_TYPES = ["Bouquet", "Arrangement", "Bundle", "Single Stem", "Vase", "Centerpiece", "Wreath"]

def generate_product_data(existing_names):
    while True:
        product_type = random.choice(PRODUCT_TYPES)
        flower = random.choice(FLOWER_NAMES)
        
        if product_type in ["Single Stem", "Bundle"]:
            name = f"{flower} {product_type}"
        else:
            adj = random.choice(ADJECTIVES)
            name = f"{adj} {flower} {product_type}"
        
        if name not in existing_names:
            break

    description = f"A stunning {name.lower()}. Perfect for any occasion, from weddings to just because."
    price = round(random.uniform(7.0, 350.0), 2)
    inventory_count = random.randint(5, 150)
    
    return {
        "name": name,
        "description": description,
        "price": price,
        "inventory_count": inventory_count
    }

def seed_database(count=300):
    print(f"Attempting to create {count} products...")
    created_count = 0
    existing_names = set()
    
    # First, get existing product names to avoid conflicts
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            products = response.json()
            for p in products:
                existing_names.add(p['name'])
        print(f"Found {len(existing_names)} existing products.")
    except requests.exceptions.ConnectionError as e:
        print(f"Error connecting to the API: {e}")
        print("Please ensure the backend service is running before seeding.")
        return

    for i in range(count):
        product_data = generate_product_data(existing_names)
        try:
            response = requests.post(API_URL, json=product_data)
            if response.status_code == 200:
                created_count += 1
                existing_names.add(product_data['name'])
                print(f"({created_count}/{count}) Created: {product_data['name']}")
            else:
                print(f"Failed to create product. Status: {response.status_code}, Response: {response.text}")
        except requests.exceptions.ConnectionError as e:
            print(f"Error connecting to the API during creation: {e}")
            return
        
        # Small delay to avoid overwhelming the server
        time.sleep(0.05)

    print(f"\nSuccessfully created {created_count} new products.")

if __name__ == "__main__":
    seed_database(300)

