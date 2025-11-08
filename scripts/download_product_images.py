#!/usr/bin/env python3
"""
Download product images from Unsplash API and update database.
Run this after seeding the database with products.
"""

import os
import sys
import requests
import psycopg2
from PIL import Image
import io
import time
from pathlib import Path
import logging

from dotenv import load_dotenv
load_dotenv(dotenv_path='../.env')  # Load from parent directory

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductImageDownloader:
    def __init__(self):
        self.unsplash_key = os.getenv('UNSPLASH_ACCESS_KEY')
        if not self.unsplash_key:
            raise ValueError("UNSPLASH_ACCESS_KEY environment variable required")

        # Database connection string
#        self.conn_string = "postgresql://user:password@db/mydatabase"
        self.conn_string = "postgresql://user:password@localhost:5432/mydatabase"

        # Image settings
        self.image_size = (400, 400)
        self.images_dir = Path('../frontend-web/public/images/products')
        self.images_dir.mkdir(parents=True, exist_ok=True)

        # Rate limiting
        self.request_delay = 0.5

    def get_products_from_db(self):
        """Fetch all products that need images."""
        try:
            conn = psycopg2.connect(self.conn_string)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, name, description 
                FROM products 
                WHERE image_url IS NULL OR image_url = ''
                ORDER BY id
            """)

            products = cursor.fetchall()
            conn.close()
            return products

        except Exception as e:
            logger.error(f"Database error: {e}")
            return []

    def search_unsplash_image(self, search_term):
        """Search for a single image on Unsplash."""
        url = "https://api.unsplash.com/search/photos"
        params = {
            'query': search_term,  # Use the actual search term now
            'per_page': 1
            # Removed: orientation and content_filter (these caused the 400 error)
        }
        headers = {
            'Authorization': f'Client-ID {self.unsplash_key}'
        }

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()

            data = response.json()
            if data['results']:
                return data['results'][0]['urls']['regular']
            return None

        except Exception as e:
            logger.error(f"Unsplash API error for '{search_term}': {e}")
            return None

    def download_and_process_image(self, image_url, filename):
        """Download image and resize to standard size."""
        try:
            response = requests.get(image_url)
            response.raise_for_status()

            # Open and resize image
            img = Image.open(io.BytesIO(response.content))
            img = img.convert('RGB')  # Ensure RGB mode
            img = img.resize(self.image_size, Image.Resampling.LANCZOS)

            # Save image
            file_path = self.images_dir / filename
            img.save(file_path, 'JPEG', quality=85, optimize=True)

            logger.info(f"Downloaded and processed: {filename}")
            return f"/images/products/{filename}"

        except Exception as e:
            logger.error(f"Error processing image {image_url}: {e}")
            return None

    def update_product_image_url(self, product_id, image_url):
        """Update product with image URL."""
        try:
            conn = psycopg2.connect(self.conn_string)
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE products SET image_url = %s WHERE id = %s",
                (image_url, product_id)
            )

            conn.commit()
            conn.close()
            logger.info(f"Updated product {product_id} with image URL")

        except Exception as e:
            logger.error(f"Error updating product {product_id}: {e}")

    def generate_search_term(self, product_name, description):
        """Generate search term based on product info."""
        # Extract flower type from name/description
        flower_types = {
            'rose': 'red rose bouquet flower',
            'tulip': 'tulip bouquet spring flower',
            'lily': 'white lily elegant flower',
            'sunflower': 'bright sunflower yellow flower',
            'carnation': 'pink carnation flower bouquet',
            'orchid': 'purple orchid exotic flower',
            'daisy': 'white daisy flower field',
            'iris': 'purple iris flower garden',
            'peony': 'pink peony flower bloom',
            'hydrangea': 'blue hydrangea flower bush'
        }

        name_lower = product_name.lower()
        desc_lower = (description or '').lower()

        # Try to match flower type
        for flower_type, search_term in flower_types.items():
            if flower_type in name_lower or flower_type in desc_lower:
                return search_term

        # Fallback to generic flower search
        return f"{product_name} flower bouquet"

    def assign_generic_images(self, products):
        """Assign generic flower images to remaining products."""
        logger.info(f"Phase 2: Assigning generic images to {len(products)} products...")

        # List of the first 50 downloaded images to reuse
        generic_images = [
            "/images/products/product-1-blushing-carnation-centerpiece.jpg",
            "/images/products/product-2-next-product.jpg",
            # Will be populated with the first 50 downloaded images
        ]

        # Get list of already downloaded images
        try:
            conn = psycopg2.connect(self.conn_string)
            cursor = conn.cursor()
            cursor.execute("SELECT image_url FROM products WHERE image_url IS NOT NULL LIMIT 50")
            generic_images = [row[0] for row in cursor.fetchall()]
            conn.close()

            logger.info(f"Found {len(generic_images)} images to reuse")

            # Assign random images from the downloaded set
            import random
            for i, (product_id, name, description) in enumerate(products):
                if generic_images:
                    # Cycle through available images
                    image_url = generic_images[i % len(generic_images)]
                    self.update_product_image_url(product_id, image_url)
                    logger.info(f"Assigned generic image to product {product_id}: {name}")

        except Exception as e:
            logger.error(f"Error assigning generic images: {e}")

    def run(self):
        """Main execution method."""
        logger.info("Starting product image download...")

        # Add image_url column if it doesn't exist
        try:
            conn = psycopg2.connect(self.conn_string)
            cursor = conn.cursor()
            cursor.execute("""
                ALTER TABLE products 
                ADD COLUMN IF NOT EXISTS image_url VARCHAR(255)
            """)
            conn.commit()
            conn.close()
            logger.info("Ensured image_url column exists")
        except Exception as e:
            logger.error(f"Error adding image_url column: {e}")
            return

        products = self.get_products_from_db()
        if not products:
            logger.info("No products found or all products already have images")
            return

        logger.info(f"Found {len(products)} products to process")

        # Process products (adjust the slice as needed for rate limiting)
        products_to_process = products[:47]  # Adjust this number based on your rate limit
        logger.info(f"Processing {len(products_to_process)} products...")

        for product_id, name, description in products_to_process:
            logger.info(f"Processing product: {name}")

            # Generate search term
            search_term = self.generate_search_term(name, description)
            logger.info(f"Searching for: {search_term}")

            # Search Unsplash
            image_url = self.search_unsplash_image(search_term)

            if image_url:
                # Generate filename
                safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-')).rstrip()
                safe_name = safe_name.replace(' ', '-').lower()
                filename = f"product-{product_id}-{safe_name}.jpg"

                # Download and process image
                local_url = self.download_and_process_image(image_url, filename)

                if local_url:
                    # Update database
                    self.update_product_image_url(product_id, local_url)
                else:
                    logger.warning(f"Failed to process image for product {product_id}")
            else:
                logger.warning(f"No image found for product {product_id}: {name}")

            # No delay since you removed it for manual rate limit management

        logger.info("Finished downloading product images")

if __name__ == "__main__":
    downloader = ProductImageDownloader()
    downloader.run()