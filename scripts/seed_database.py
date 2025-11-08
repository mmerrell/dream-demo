import requests
import random
import time
import os

API_URL = "http://localhost:8000/products/"

ADJECTIVES = ["Vibrant", "Classic", "Elegant", "Rustic", "Sunshine", "Midnight", "Enchanted", "Jubilant", "Serene",
              "Blushing", "Golden", "Winter"]
FLOWER_NAMES = ["Rose", "Lily", "Tulip", "Orchid", "Daisy", "Sunflower", "Peony", "Hydrangea", "Carnation", "Freesia",
                "Lavender", "Marigold"]
PRODUCT_TYPES = ["Bouquet", "Arrangement", "Bundle", "Single Stem", "Vase", "Centerpiece", "Wreath"]


def get_random_image():
    """Get a random product image if available."""
    images_dir = 'frontend-web/public/images/products'

    if not os.path.exists(images_dir):
        return None

    available_images = os.listdir(images_dir)
    image_files = [f for f in available_images if f.endswith('.jpg')]

    if not image_files:
        return None

    random_image = random.choice(image_files)
    return f'/images/products/{random_image}'


def check_api_supports_images():
    """Check if the API response includes image_url field for backward compatibility."""
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            products = response.json()
            if products and len(products) > 0:
                # Check if the field exists in the response, regardless of its value
                return "image_url" in products[0]
            else:
                # No products exist yet - check by trying to create a test product
                # and see if the API accepts the image_url field
                test_product = {
                    "name": "TEST_PRODUCT_DELETE_ME",
                    "description": "Test product",
                    "price": 1.0,
                    "inventory_count": 1,
                    "image_url": "/test/image.jpg"
                }

                test_response = requests.post(API_URL, json=test_product)
                if test_response.status_code == 200:
                    # Clean up the test product
                    created_product = test_response.json()
                    if 'id' in created_product:
                        requests.delete(f"{API_URL.rstrip('/')}/{created_product['id']}")
                    return True
                else:
                    return False
    except:
        pass
    return False

def generate_product_data(existing_names, include_images=False):
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

    product_data = {
        "name": name,
        "description": description,
        "price": price,
        "inventory_count": inventory_count
    }

    # Add image if supported and available
    if include_images:
        image_url = get_random_image()
        if image_url:
            product_data["image_url"] = image_url

    return product_data


def seed_database(count=300):
    print(f"Attempting to create {count} products...")
    created_count = 0
    existing_names = set()

    # Check if API supports images
    supports_images = check_api_supports_images()
    if supports_images:
        print("API supports images - will assign random images to products")
    else:
        print("API doesn't support images - creating products without images")

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
        product_data = generate_product_data(existing_names, include_images=supports_images)
        try:
            response = requests.post(API_URL, json=product_data)
            if response.status_code == 200:
                created_count += 1
                existing_names.add(product_data['name'])
                image_info = f" (with image)" if product_data.get('image_url') else ""
                print(f"({created_count}/{count}) Created: {product_data['name']}{image_info}")
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