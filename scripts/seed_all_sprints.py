#!/usr/bin/env python3
import requests
import random
import time
import sys

# Sprint configurations
SPRINTS = {
    "sprint-1": "http://sprint-1.dreamdemo.xyz:8000/products/",
    "sprint-2": "http://sprint-2.dreamdemo.xyz:8000/products/", 
    "sprint-3": "http://sprint-3.dreamdemo.xyz:8000/products/",
    # Uncomment when sprint-4 is working:
    # "sprint-4": "http://sprint-4.dreamdemo.xyz:8000/products/"
}

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

def test_api_connection(api_url):
    """Test if the API is accessible"""
    try:
        response = requests.get(api_url, timeout=10)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def seed_sprint(sprint_name, api_url, count=50):
    """Seed a specific sprint with products"""
    print(f"\n{'='*50}")
    print(f"Seeding {sprint_name.upper()}")
    print(f"API URL: {api_url}")
    print(f"{'='*50}")
    
    # Test connection first
    if not test_api_connection(api_url):
        print(f"❌ Cannot connect to {sprint_name} API. Skipping...")
        return 0
    
    created_count = 0
    existing_names = set()
    
    # Get existing products to avoid duplicates
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            products = response.json()
            for p in products:
                existing_names.add(p['name'])
        print(f"📋 Found {len(existing_names)} existing products.")
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Warning: Could not fetch existing products: {e}")

    # Create new products
    for i in range(count):
        product_data = generate_product_data(existing_names)
        try:
            response = requests.post(api_url, json=product_data, timeout=10)
            if response.status_code == 200:
                created_count += 1
                existing_names.add(product_data['name'])
                print(f"✅ ({created_count}/{count}) Created: {product_data['name']}")
            else:
                print(f"❌ Failed to create product. Status: {response.status_code}, Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating product: {e}")
            continue
        
        # Small delay to avoid overwhelming the server
        time.sleep(0.1)

    print(f"\n✨ Successfully created {created_count} new products for {sprint_name}.")
    return created_count

def seed_all_sprints(count_per_sprint=50):
    """Seed all available sprints"""
    print("🌱 Starting multi-sprint seeding process...")
    print(f"Target: {count_per_sprint} products per sprint")
    
    total_created = 0
    successful_sprints = 0
    
    for sprint_name, api_url in SPRINTS.items():
        created = seed_sprint(sprint_name, api_url, count_per_sprint)
        total_created += created
        if created > 0:
            successful_sprints += 1
    
    print(f"\n{'='*60}")
    print("🎉 SEEDING COMPLETE")
    print(f"{'='*60}")
    print(f"✅ Successfully seeded {successful_sprints}/{len(SPRINTS)} sprints")
    print(f"🌸 Total products created: {total_created}")
    
    if successful_sprints < len(SPRINTS):
        failed_sprints = [name for name in SPRINTS.keys() if not test_api_connection(SPRINTS[name])]
        print(f"❌ Failed sprints: {', '.join(failed_sprints)}")
        print("   Check that these sprint APIs are running and accessible")

def seed_single_sprint(sprint_name, count=50):
    """Seed a single specific sprint"""
    if sprint_name not in SPRINTS:
        print(f"❌ Unknown sprint: {sprint_name}")
        print(f"Available sprints: {', '.join(SPRINTS.keys())}")
        return
    
    api_url = SPRINTS[sprint_name]
    seed_sprint(sprint_name, api_url, count)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments - seed all sprints
        seed_all_sprints(50)
    elif len(sys.argv) == 2:
        # Single sprint name provided
        sprint_name = sys.argv[1]
        seed_single_sprint(sprint_name)
    elif len(sys.argv) == 3:
        # Sprint name and count provided
        sprint_name = sys.argv[1]
        try:
            count = int(sys.argv[2])
            seed_single_sprint(sprint_name, count)
        except ValueError:
            print("❌ Count must be a number")
            print("Usage: python seed_all_sprints.py [sprint-name] [count]")
    else:
        print("Usage:")
        print("  python seed_all_sprints.py                    # Seed all sprints (50 each)")
        print("  python seed_all_sprints.py sprint-1           # Seed specific sprint (50 products)")
        print("  python seed_all_sprints.py sprint-1 100       # Seed specific sprint (100 products)")
