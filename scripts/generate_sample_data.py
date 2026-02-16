#!/usr/bin/env python
"""
Populate the IntelliQuery AI database with realistic e-commerce sample data.

Generates:
- 5 regions
- 1 000 customers
- 200 products (across 6 categories)
- 5 000 orders  (spanning ~2 years, with seasonal trends)
- 10 000+ order items

Usage::

    python scripts/generate_sample_data.py
"""

from __future__ import annotations

import random
import sys
from datetime import date, timedelta
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config.settings import Settings
from src.database.connection import get_engine, session_scope, test_connection
from src.database.models import Base, Customer, Order, OrderItem, Product, Region

# ── Seed for reproducibility ────────────────────────────────────────────────
random.seed(42)

# ── Reference data ──────────────────────────────────────────────────────────

REGIONS = [
    ("North", "United States"),
    ("South", "United States"),
    ("East", "United States"),
    ("West", "United States"),
    ("Central", "United States"),
]

FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "Michael", "Jennifer", "William",
    "Linda", "David", "Elizabeth", "Richard", "Barbara", "Joseph", "Susan",
    "Thomas", "Jessica", "Charles", "Sarah", "Christopher", "Karen",
    "Daniel", "Lisa", "Matthew", "Nancy", "Anthony", "Betty", "Mark",
    "Margaret", "Donald", "Sandra", "Steven", "Ashley", "Paul", "Kimberly",
    "Andrew", "Emily", "Joshua", "Donna", "Kenneth", "Michelle", "Kevin",
    "Carol", "Brian", "Amanda", "George", "Dorothy", "Timothy", "Melissa",
    "Ronald", "Deborah", "Edward", "Stephanie", "Jason", "Rebecca", "Jeffrey",
    "Sharon", "Ryan", "Laura", "Jacob", "Cynthia", "Gary", "Kathleen",
    "Nicholas", "Amy", "Eric", "Angela", "Jonathan", "Shirley", "Stephen",
    "Anna", "Larry", "Brenda", "Justin", "Pamela", "Scott", "Emma",
    "Brandon", "Nicole", "Benjamin", "Helen", "Samuel", "Samantha",
    "Raymond", "Katherine", "Gregory", "Christine", "Frank", "Debra",
    "Alexander", "Rachel", "Patrick", "Carolyn", "Jack", "Janet",
    "Dennis", "Catherine", "Jerry", "Maria", "Tyler", "Heather",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
    "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Phillips", "Evans", "Turner", "Diaz", "Parker",
    "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales",
    "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper",
    "Peterson", "Bailey", "Reed", "Kelly", "Howard", "Ramos", "Kim",
    "Cox", "Ward", "Richardson", "Watson", "Brooks", "Chavez", "Wood",
    "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes", "Price",
    "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long", "Ross",
]

CATEGORIES: dict[str, list[tuple[str, list[str]]]] = {
    "Technology": [
        ("Laptops", [
            "ProBook Laptop 15\"", "UltraSlim Notebook", "GamerX Laptop",
            "Business Elite Laptop", "ChromeBook Lite", "Creator Studio Laptop",
        ]),
        ("Phones", [
            "Galaxy Pro X", "iPhone Ultra", "Pixel Smart 7", "OnePlus Ace",
            "Redmi Note Pro", "Motorola Edge",
        ]),
        ("Accessories", [
            "Wireless Mouse", "Mechanical Keyboard", "USB-C Hub 7-in-1",
            "Laptop Stand Adjustable", "Webcam HD 1080p", "Noise-Cancel Headset",
            "Bluetooth Speaker", "Portable Charger 20K",
        ]),
    ],
    "Furniture": [
        ("Chairs", [
            "Ergonomic Office Chair", "Executive Leather Chair", "Standing Desk Stool",
            "Mesh Task Chair", "Gaming Chair Pro",
        ]),
        ("Desks", [
            "Standing Desk Electric", "L-Shape Corner Desk", "Compact Writing Desk",
            "Executive Mahogany Desk", "Folding Table Portable",
        ]),
        ("Storage", [
            "3-Drawer File Cabinet", "Bookshelf Modern 5-Tier", "Wall Shelf Set",
            "Storage Ottoman", "Cube Organiser 9-Cell",
        ]),
    ],
    "Office Supplies": [
        ("Paper", [
            "Printer Paper A4 500ct", "Legal Pad Yellow 12pk", "Sticky Notes 3x3 12pk",
            "Notebook Spiral 5-Subject", "Card Stock White 100ct",
        ]),
        ("Writing", [
            "Ballpoint Pen 12-Pack", "Gel Pen Assorted 10pk", "Whiteboard Markers 8pk",
            "Highlighter Set 6-Color", "Mechanical Pencils 0.7mm",
        ]),
        ("Organisation", [
            "Binder Clips Assorted 100ct", "File Folders Manila 50ct",
            "Desktop Organiser Mesh", "Label Maker Portable",
            "Desk Calendar 2024",
        ]),
    ],
    "Clothing": [
        ("Men", [
            "Slim Fit Dress Shirt", "Chino Pants Classic", "Crew Neck T-Shirt 3pk",
            "Blazer Tailored Fit", "Running Shoes Flyknit",
        ]),
        ("Women", [
            "Blouse Silk V-Neck", "High-Waist Jeans", "Wrap Dress Floral",
            "Cardigan Cashmere", "Sneakers Canvas Low",
        ]),
        ("Accessories", [
            "Leather Belt Classic", "Wool Scarf Plaid", "Sunglasses Aviator",
            "Watch Stainless Steel", "Backpack Waterproof",
        ]),
    ],
    "Food & Beverages": [
        ("Coffee & Tea", [
            "Colombian Coffee Beans 1lb", "Green Tea Organic 100ct",
            "Espresso Pods Compatible 50ct", "Matcha Powder Ceremonial",
            "Chai Latte Mix 20ct",
        ]),
        ("Snacks", [
            "Mixed Nuts Deluxe 2lb", "Protein Bar Variety 12pk",
            "Dark Chocolate 72% 4-Pack", "Trail Mix Organic 1lb",
            "Rice Crackers Sea Salt 6pk",
        ]),
        ("Beverages", [
            "Sparkling Water 24-Pack", "Energy Drink Sugar-Free 12pk",
            "Coconut Water Pure 12pk", "Cold Brew Concentrate 32oz",
            "Kombucha Variety 6pk",
        ]),
    ],
    "Health & Beauty": [
        ("Skincare", [
            "Moisturiser SPF30 50ml", "Vitamin C Serum 30ml",
            "Face Wash Gentle 200ml", "Eye Cream Anti-Age 15ml",
            "Sunscreen Sport SPF50 100ml",
        ]),
        ("Hair Care", [
            "Shampoo Volumising 400ml", "Conditioner Argan Oil 400ml",
            "Hair Dryer Ionic Pro", "Styling Gel Strong Hold 250ml",
            "Dry Shampoo Spray 200ml",
        ]),
        ("Wellness", [
            "Multivitamin Daily 90ct", "Yoga Mat Premium 6mm",
            "Foam Roller 18\"", "Resistance Bands Set 5",
            "Water Bottle Insulated 32oz",
        ]),
    ],
}

STATUSES = ["Delivered", "Shipped", "Processing", "Cancelled"]
STATUS_WEIGHTS = [0.65, 0.15, 0.12, 0.08]

SEGMENTS = ["Gold", "Silver", "Bronze"]
SEGMENT_WEIGHTS = [0.15, 0.35, 0.50]


# ── Helpers ──────────────────────────────────────────────────────────────────

def _random_email(first: str, last: str) -> str:
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "proton.me"]
    tag = random.randint(1, 999)
    return f"{first.lower()}.{last.lower()}{tag}@{random.choice(domains)}"


def _price_for_category(category: str) -> tuple[float, float]:
    """Return (price, cost) with realistic margins per category."""
    ranges: dict[str, tuple[float, float]] = {
        "Technology": (29.99, 2499.99),
        "Furniture": (49.99, 1299.99),
        "Office Supplies": (2.99, 79.99),
        "Clothing": (14.99, 299.99),
        "Food & Beverages": (3.99, 49.99),
        "Health & Beauty": (5.99, 149.99),
    }
    lo, hi = ranges.get(category, (9.99, 499.99))
    price = round(random.uniform(lo, hi), 2)
    margin = random.uniform(0.20, 0.55)
    cost = round(price * (1 - margin), 2)
    return price, cost


def _seasonal_order_weight(d: date) -> float:
    """Return a weight that makes Q4 (holiday season) busier."""
    month = d.month
    if month in (11, 12):
        return 2.5
    if month in (1, 6, 7):
        return 1.3
    return 1.0


# ── Main generator ──────────────────────────────────────────────────────────

def main() -> None:
    Settings.validate()

    if not test_connection():
        print("Error: Cannot connect to the database. Check DATABASE_URL in .env")
        sys.exit(1)

    engine = get_engine()
    # Ensure tables exist
    Base.metadata.create_all(engine)

    with session_scope() as session:
        # ── Check if data already exists ─────────────────────────────
        existing = session.query(Region).count()
        if existing > 0:
            print("Warning: Data already exists. Skipping generation.")
            print("   Drop tables first if you want to regenerate.")
            return

        # -- Regions --------------------------------------------------
        print("Inserting regions ...")
        region_objs: list[Region] = []
        for name, country in REGIONS:
            r = Region(region_name=name, country=country)
            session.add(r)
            region_objs.append(r)
        session.flush()  # get IDs

        # -- Products -------------------------------------------------
        print("Inserting products ...")
        product_objs: list[Product] = []
        for category, subcats in CATEGORIES.items():
            for sub_name, product_names in subcats:
                for pname in product_names:
                    price, cost = _price_for_category(category)
                    p = Product(
                        product_name=pname,
                        category=category,
                        sub_category=sub_name,
                        price=price,
                        cost=cost,
                    )
                    session.add(p)
                    product_objs.append(p)
        session.flush()
        print(f"   -> {len(product_objs)} products")

        # -- Customers ------------------------------------------------
        print("Inserting customers ...")
        customer_objs: list[Customer] = []
        start_date = date.today() - timedelta(days=730)
        for i in range(1000):
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            reg_date = start_date + timedelta(days=random.randint(0, 700))
            c = Customer(
                customer_name=f"{first} {last}",
                email=_random_email(first, last),
                region_id=random.choice(region_objs).region_id,
                registration_date=reg_date,
                customer_segment=random.choices(SEGMENTS, SEGMENT_WEIGHTS)[0],
            )
            session.add(c)
            customer_objs.append(c)
        session.flush()

        # -- Orders & Order Items -------------------------------------
        print("Inserting orders & order items ...")
        today = date.today()
        order_start = today - timedelta(days=730)
        total_items = 0

        # Build a pool of weighted dates for seasonal trends
        date_pool: list[date] = []
        d = order_start
        while d <= today:
            weight = _seasonal_order_weight(d)
            date_pool.extend([d] * int(weight * 10))
            d += timedelta(days=1)

        for _ in range(5000):
            cust = random.choice(customer_objs)
            order_date = random.choice(date_pool)
            ship_delay = random.randint(1, 14)
            status = random.choices(STATUSES, STATUS_WEIGHTS)[0]
            ship_date = (
                order_date + timedelta(days=ship_delay)
                if status in ("Delivered", "Shipped")
                else None
            )

            order = Order(
                customer_id=cust.customer_id,
                order_date=order_date,
                ship_date=ship_date,
                status=status,
            )
            session.add(order)
            session.flush()

            # 1-5 items per order
            n_items = random.randint(1, 5)
            chosen_products = random.sample(
                product_objs, min(n_items, len(product_objs))
            )
            for prod in chosen_products:
                qty = random.randint(1, 10)
                discount = random.choice([0, 0, 0, 0.05, 0.10, 0.15, 0.20])
                item = OrderItem(
                    order_id=order.order_id,
                    product_id=prod.product_id,
                    quantity=qty,
                    unit_price=float(prod.price),
                    discount=discount,
                )
                session.add(item)
                total_items += 1

        print(f"   -> 5000 orders, {total_items:,} order items")

    print()
    print("Sample data generated successfully!")


if __name__ == "__main__":
    main()
