from django.core.management.base import BaseCommand
from models.products import Product
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with sample products'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database with sample products...')
        
        # Create sample products
        products_data = [
            {
                'name': 'Laptop',
                'description': 'High-performance laptop with 16GB RAM and 512GB SSD',
                'price': 999.99,
                'stock_quantity': 50,
                'is_active': True
            },
            {
                'name': 'Wireless Mouse',
                'description': 'Ergonomic wireless mouse with 2.4GHz connectivity',
                'price': 29.99,
                'stock_quantity': 200,
                'is_active': True
            },
            {
                'name': 'Mechanical Keyboard',
                'description': 'RGB mechanical keyboard with blue switches',
                'price': 89.99,
                'stock_quantity': 100,
                'is_active': True
            },
            {
                'name': 'USB-C Hub',
                'description': '7-in-1 USB-C hub with HDMI, USB 3.0, and SD card reader',
                'price': 49.99,
                'stock_quantity': 150,
                'is_active': True
            },
            {
                'name': 'Wireless Headphones',
                'description': 'Noise-cancelling Bluetooth headphones with 30-hour battery',
                'price': 199.99,
                'stock_quantity': 75,
                'is_active': True
            },
            {
                'name': 'Webcam 1080p',
                'description': 'Full HD webcam with built-in microphone',
                'price': 59.99,
                'stock_quantity': 120,
                'is_active': True
            },
            {
                'name': 'Desk Lamp',
                'description': 'LED desk lamp with adjustable brightness and color temperature',
                'price': 39.99,
                'stock_quantity': 80,
                'is_active': True
            },
            {
                'name': 'Laptop Stand',
                'description': 'Aluminum laptop stand with adjustable height',
                'price': 34.99,
                'stock_quantity': 90,
                'is_active': True
            },
            {
                'name': 'External SSD 1TB',
                'description': 'Portable external SSD with USB-C, 1TB storage',
                'price': 129.99,
                'stock_quantity': 60,
                'is_active': True
            },
            {
                'name': 'Monitor 27"',
                'description': '27-inch 4K monitor with HDR support',
                'price': 399.99,
                'stock_quantity': 40,
                'is_active': True
            },
        ]
        
        created_count = 0
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults=product_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'  ✓ Created: {product.name}')
            else:
                self.stdout.write(f'  - Exists: {product.name}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully created {created_count} new products!'))
        self.stdout.write(f'Total products in database: {Product.objects.count()}')
