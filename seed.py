#!/usr/bin/env python
import json
import random
from datetime import datetime, timezone
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.product import Category, Product, Review
from app.models.order import Order, OrderItem

def seed():
    app = create_app()
    with app.app_context():
        print("Dropping and re-creating database tables...")
        db.drop_all()
        db.create_all()

        print("Seeding Categories...")
        categories_data = [
            {"name": "Men's Tops", "slug": "mens-tops"},
            {"name": "Men's Bottoms", "slug": "mens-bottoms"},
            {"name": "Women's Tops", "slug": "womens-tops"},
            {"name": "Women's Bottoms", "slug": "womens-bottoms"},
            {"name": "Outerwear", "slug": "outerwear"},
            {"name": "Accessories", "slug": "accessories"},
            {"name": "Footwear", "slug": "footwear"},
        ]

        categories = {}
        for cat in categories_data:
            c = Category(name=cat["name"], slug=cat["slug"])
            db.session.add(c)
            categories[cat["slug"]] = c
        
        db.session.flush()

        print("Seeding Users...")
        admin = User(
            email='admin@atelier.com',
            full_name='Admin User',
            is_admin=True,
            addresses=json.dumps([{
                "title": "Headquarters",
                "street": "100 Fashion Avenue",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "country": "USA"
            }])
        )
        admin.set_password('adminpass123')

        customer = User(
            email='customer@example.com',
            full_name='Alex Morgan',
            is_admin=False,
            addresses=json.dumps([{
                "title": "Home",
                "street": "123 Main Street, Apt 4B",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "country": "USA"
            }])
        )
        customer.set_password('customer123')

        jane = User(
            email='jane@example.com',
            full_name='Jane Doe',
            is_admin=False,
            addresses=json.dumps([{
                "title": "Apartment",
                "street": "456 Oak Lane",
                "city": "Brooklyn",
                "state": "NY",
                "zip": "11201",
                "country": "USA"
            }])
        )
        jane.set_password('jane123')

        db.session.add_all([admin, customer, jane])
        db.session.flush()

        print("Seeding Products...")
        products_data = [
            # Men's Tops
            {
                "category_slug": "mens-tops",
                "name": "Classic Oxford Button-Down Shirt",
                "description": "A timeless wardrobe staple crafted from 100% premium woven cotton oxford fabric. Features a crisp button-down collar, single chest pocket, and a tailored regular fit. Perfect for layering or wearing solo from desk to dinner.",
                "price": 69.99,
                "images": json.dumps([
                    "https://picsum.photos/seed/oxford-shirt-1/600/800",
                    "https://picsum.photos/seed/oxford-shirt-2/600/800",
                    "https://picsum.photos/seed/oxford-shirt-3/600/800"
                ]),
                "sizes": json.dumps(["S", "M", "L", "XL", "XXL"]),
                "colors": json.dumps(["White", "Light Blue", "Pink"]),
                "stock": 25
            },
            {
                "category_slug": "mens-tops",
                "name": "Essential Crewneck T-Shirt",
                "description": "Crafted from ultra-soft combed ring-spun jersey cotton for everyday comfort. Pre-shrunk with a classic relaxed fit and reinforced double-stitched seams. An indispensable foundation piece for any casual outfit.",
                "price": 29.99,
                "images": json.dumps([
                    "https://picsum.photos/seed/crewneck-tee-1/600/800",
                    "https://picsum.photos/seed/crewneck-tee-2/600/800",
                    "https://picsum.photos/seed/crewneck-tee-3/600/800"
                ]),
                "sizes": json.dumps(["XS", "S", "M", "L", "XL"]),
                "colors": json.dumps(["Black", "White", "Heather Grey", "Navy"]),
                "stock": 45
            },
            {
                "category_slug": "mens-tops",
                "name": "Heavyweight Fleece Hoodie",
                "description": "Constructed from 400gsm dense cotton-poly blend fleece with a double-lined hood. Features deep kangaroo pockets, ribbed side panels, and durable metal-tipped drawstrings. Designed to keep you warm with an urban silhouette.",
                "price": 89.99,
                "images": json.dumps([
                    "https://picsum.photos/seed/fleece-hoodie-1/600/800",
                    "https://picsum.photos/seed/fleece-hoodie-2/600/800",
                    "https://picsum.photos/seed/fleece-hoodie-3/600/800"
                ]),
                "sizes": json.dumps(["S", "M", "L", "XL"]),
                "colors": json.dumps(["Charcoal", "Olive", "Black"]),
                "stock": 0
            },
            {
                "category_slug": "mens-tops",
                "name": "Merino Wool Polo Shirt",
                "description": "Spun from fine Australian merino wool with naturally moisture-wicking and temperature-regulating properties. Styled with a three-button placket and ribbed collar. Offers elevated sophistication for business casual attire.",
                "price": 119.99,
                "images": json.dumps([
                    "https://picsum.photos/seed/merino-polo-1/600/800",
                    "https://picsum.photos/seed/merino-polo-2/600/800",
                    "https://picsum.photos/seed/merino-polo-3/600/800"
                ]),
                "sizes": json.dumps(["S", "M", "L", "XL"]),
                "colors": json.dumps(["Navy", "Burgundy", "Forest Green"]),
                "stock": 3
            },

            # Men's Bottoms
            {
                "category_slug": "mens-bottoms",
                "name": "Slim Fit Stretch Chinos",
                "description": "Engineered from mid-weight cotton twill infused with subtle elastane for flexible mobility. Features slant front pockets, welt rear pockets, and a tapered narrow leg opening. Sharp enough for the office and casual enough for weekends.",
                "price": 79.99,
                "images": json.dumps([
                    "https://picsum.photos/seed/slim-chinos-1/600/800",
                    "https://picsum.photos/seed/slim-chinos-2/600/800",
                    "https://picsum.photos/seed/slim-chinos-3/600/800"
                ]),
                "sizes": json.dumps(["30", "32", "34", "36"]),
                "colors": json.dumps(["Khaki", "Navy", "Olive", "Charcoal"]),
                "stock": 30
            },
            {
                "category_slug": "mens-bottoms",
                "name": "Selvedge Denim Jeans",
                "description": "Cut from 13.5oz raw Japanese selvedge denim that breaks in uniquely over time. Built with copper rivets, button fly, and traditional red-line selvedge seam tape. A premium staple for true denim enthusiasts.",
                "price": 149.99,
                "images": json.dumps([
                    "https://picsum.photos/seed/selvedge-jeans-1/600/800",
                    "https://picsum.photos/seed/selvedge-jeans-2/600/800",
                    "https://picsum.photos/seed/selvedge-jeans-3/600/800"
                ]),
                "sizes": json.dumps(["30", "32", "34", "36"]),
                "colors": json.dumps(["Indigo Raw", "Washed Black"]),
                "stock": 18
            },
            {
                "category_slug": "mens-bottoms",
                "name": "Tailored Wool Trousers",
                "description": "Precision tailored from breathable Italian virgin wool with a flat-front design. Finished with an adjustable internal drawstring waistband and pressed leg creases. Ideal for modern formal and smart-casual styling.",
                "price": 139.99,
                "images": json.dumps([
                    "https://picsum.photos/seed/wool-trousers-1/600/800",
                    "https://picsum.photos/seed/wool-trousers-2/600/800",
                    "https://picsum.photos/seed/wool-trousers-3/600/800"
                ]),
                "sizes": json.dumps(["30", "32", "34", "36"]),
                "colors": json.dumps(["Charcoal", "Navy", "Black"]),
                "stock": 2
            },
            {
                "category_slug": "mens-bottoms",
                "name": "Relaxed Linen Drawstring Pants",
                "description": "Woven from 100% pure European flax linen for unmatched breathability in warm weather. Features an elasticated drawcord waist, wide leg cut, and deep side pockets. Perfect for beach vacations and relaxed summer days.",
                "price": 69.99,
                "images": json.dumps([
                    "https://picsum.photos/seed/linen-pants-1/600/800",
                    "https://picsum.photos/seed/linen-pants-2/600/800",
                    "https://picsum.photos/seed/linen-pants-3/600/800"
                ]),
                "sizes": json.dumps(["S", "M", "L", "XL"]),
                "colors": json.dumps(["Natural Flax", "White", "Navy"]),
                "stock": 12
            },

            # Women's Tops
            {
                "category_slug": "womens-tops",
                "name": "Silk Button-Front Blouse",
                "description": "Elegantly drape-tailored from 100% mulberry silk crepe de chine. Features hidden mother-of-pearl buttons, fluid relaxed sleeves, and a curved hemline. Adds instant luxury to trousers or denim.",
                "price": 159.99,
                "images": json.dumps([
                    "https://picsum.photos/seed/silk-blouse-1/600/800",
                    "https://picsum.photos/seed/silk-blouse-2/600/800",
                    "https://picsum.photos/seed/silk-blouse-3/600/800"
                ]),
                "sizes": json.dumps(["XS", "S", "M", "L"]),
                "colors": json.dumps(["Ivory", "Champagne", "Black"]),
                "stock": 15
            },
            {
                "category_slug": "womens-tops",
                "name": "Ribbed Knit Tank Top",
                "description": "Spun from a soft organic cotton rib with high elasticity and form-fitting silhouette. Designed with a clean scoop neckline and wide bra-friendly shoulder straps. An effortless elevated essential for layering.",
                "price": 34.99,
                "images": json.dumps([
                    "https://picsum.photos/seed/ribbed-tank-1/600/800",
                    "https://picsum.photos/seed/ribbed-tank-2/600/800",
                    "https://picsum.photos/seed/ribbed-tank-3/600/800"
                ]),
                "sizes": json.dumps(["XS", "S", "M", "L"]),
                "colors": json.dumps(["White", "Black", "Taupe", "Sage"]),
                "stock": 40
            },
            {
                "category_slug": "womens-tops",
                "name": "Oversized Cable-Knit Sweater",
                "description": "Chunkily knitted from plush wool blend yarns featuring intricate traditional cable patterns. Cut in a boxy oversized fit with dropped shoulders and thick ribbed trims. Cozy comfort meets high fashion.",
                "price": 129.99,
                "images": json.dumps([
                    "https://picsum.photos/seed/cable-sweater-1/600/800",
                    "https://picsum.photos/seed/cable-sweater-2/600/800",
                    "https://picsum.photos/seed/cable-sweater-3/600/800"
                ]),
                "sizes": json.dumps(["XS", "S", "M", "L"]),
                "colors": json.dumps(["Cream", "Oatmeal", "Soft Pink"]),
                "stock": 0
            },
            {
                "category_slug": "womens-tops",
                "name": "Cropped Graphic Sweatshirt",
                "description": "Made from vintage-washed French terry cotton with a relaxed drop-shoulder cut. Features a minimalist tonal embroidery across the chest and raw edge hem. A stylish piece for athleisure looks.",
                "price": 59.99,
                "images": json.dumps([
                    "https://picsum.photos/seed/cropped-sweatshirt-1/600/800",
                    "https://picsum.photos/seed/cropped-sweatshirt-2/600/800",
                    "https://picsum.photos/seed/cropped-sweatshirt-3/600/800"
                ]),
                "sizes": json.dumps(["XS", "S", "M", "L"]),
                "colors": json.dumps(["Washed Rose", "Heather Grey", "Off-White"]),
                "stock": 22
            },

            # Women's Bottoms
            {
                "category_slug": "womens-bottoms",
                "name": "High-Waisted Wide-Leg Trousers",
                "description": "Tailored with front pleats and a flattering ultra-high rise that elongates the silhouette. Crafted from a structured fluid crepe fabric with side slant pockets. Transitions effortlessly from work to dinner.",
                "price": 119.99,
                "images": json.dumps([
                    "https://picsum.photos/seed/wide-trousers-1/600/800",
                    "https://picsum.photos/seed/wide-trousers-2/600/800",
                    "https://picsum.photos/seed/wide-trousers-3/600/800"
                ]),
                "sizes": json.dumps(["2", "4", "6", "8", "10", "12"]),
                "colors": json.dumps(["Black", "Terracotta", "Cream"]),
                "stock": 20
            },
            {
                "category_slug": "womens-bottoms",
                "name": "Straight Leg Ankle Jeans",
                "description": "Classic vintage-inspired 90s straight leg cut crafted from rigid organic cotton denim. Features a high waist, light distressing along the pockets, and a clean ankle crop hem. The ultimate go-to denim.",
                "price": 98.99,
                "images": json.dumps([
                    "https://picsum.photos/seed/straight-jeans-1/600/800",
                    "https://picsum.photos/seed/straight-jeans-2/600/800",
                    "https://picsum.photos/seed/straight-jeans-3/600/800"
                ]),
                "sizes": json.dumps(["24", "25", "26", "27", "28", "29", "30"]),
                "colors": json.dumps(["Medium Vintage Wash", "Light Wash", "Black"]),
                "stock": 28
            },
            {
                "category_slug": "womens-bottoms",
                "name": "Pleated Midi Skirt",
                "description": "Designed with crisp accordion pleats that move gracefully with every step. Cut from a lightweight satin weave with a subtle lustre and elasticated waistband. Elegant and versatile across seasons.",
                "price": 84.99,
                "images": json.dumps([
                    "https://picsum.photos/seed/midi-skirt-1/600/800",
                    "https://picsum.photos/seed/midi-skirt-2/600/800",
                    "https://picsum.photos/seed/midi-skirt-3/600/800"
                ]),
                "sizes": json.dumps(["XS", "S", "M", "L"]),
                "colors": json.dumps(["Emerald Green", "Navy", "Champagne"]),
                "stock": 4
            },
            {
                "category_slug": "womens-bottoms",
                "name": "Tailored Linen Shorts",
                "description": "Breathable pure linen shorts with high-rise waist and subtle front pleating. Features side pockets and matching removable tie belt. Ideal for warm weather sophistication.",
                "price": 49.99,
                "images": json.dumps([
                    "https://picsum.photos/seed/linen-shorts-1/600/800",
                    "https://picsum.photos/seed/linen-shorts-2/600/800",
                    "https://picsum.photos/seed/linen-shorts-3/600/800"
                ]),
                "sizes": json.dumps(["XS", "S", "M", "L"]),
                "colors": json.dumps(["Sand", "White", "Sage"]),
                "stock": 16
            },

            # Outerwear
            {
                "category_slug": "outerwear",
                "name": "Classic Double-Breasted Trench Coat",
                "description": "Iconic outerwear crafted from water-resistant cotton gabardine fabric. Features traditional storm flaps, epaulettes, waist belt with buckled closure, and back vent. A timeless investment piece for rainy days.",
                "price": 249.99,
                "images": json.dumps([
                    "https://picsum.photos/seed/trench-coat-1/600/800",
                    "https://picsum.photos/seed/trench-coat-2/600/800",
                    "https://picsum.photos/seed/trench-coat-3/600/800"
                ]),
                "sizes": json.dumps(["XS", "S", "M", "L", "XL"]),
                "colors": json.dumps(["Beige", "Black", "Navy"]),
                "stock": 10
            },
            {
                "category_slug": "outerwear",
                "name": "Wool-Blend Overcoat",
                "description": "Tailored from heavy Italian wool blend cloth for ultimate warmth and structure. Built with notch lapels, three-button front closure, and smooth satin lining. Elevates formal tailored wear and casual knits alike.",
                "price": 299.99,
                "images": json.dumps([
                    "https://picsum.photos/seed/wool-overcoat-1/600/800",
                    "https://picsum.photos/seed/wool-overcoat-2/600/800",
                    "https://picsum.photos/seed/wool-overcoat-3/600/800"
                ]),
                "sizes": json.dumps(["S", "M", "L", "XL"]),
                "colors": json.dumps(["Camel", "Charcoal", "Black"]),
                "stock": 8
            },
            {
                "category_slug": "outerwear",
                "name": "Quilted Lightweight Puffer Jacket",
                "description": "Insulated with recycled down-alternative fill housed in a durable ripstop nylon shell. Designed with a stand collar, zippered side pockets, and packable pouch included. Lightweight yet exceptionally warm.",
                "price": 139.99,
                "images": json.dumps([
                    "https://picsum.photos/seed/puffer-jacket-1/600/800",
                    "https://picsum.photos/seed/puffer-jacket-2/600/800",
                    "https://picsum.photos/seed/puffer-jacket-3/600/800"
                ]),
                "sizes": json.dumps(["XS", "S", "M", "L", "XL"]),
                "colors": json.dumps(["Matte Black", "Olive Drab", "Navy"]),
                "stock": 15
            },
            {
                "category_slug": "outerwear",
                "name": "Heritage Leather Biker Jacket",
                "description": "Crafted from butter-soft lambskin leather with silver hardware and asymmetric zip front. Features zippered cuffs, snap lapels, and smooth satin lining. Adds an iconic edge to any outfit.",
                "price": 289.99,
                "images": json.dumps([
                    "https://picsum.photos/seed/biker-jacket-1/600/800",
                    "https://picsum.photos/seed/biker-jacket-2/600/800",
                    "https://picsum.photos/seed/biker-jacket-3/600/800"
                ]),
                "sizes": json.dumps(["S", "M", "L", "XL"]),
                "colors": json.dumps(["Black", "Dark Brown"]),
                "stock": 3
            },

            # Accessories
            {
                "category_slug": "accessories",
                "name": "Leather Crossbody Bag",
                "description": "Handcrafted from full-grain Italian leather with magnetic flap closure. Internal zip pocket, phone sleeve, and adjustable shoulder strap. Compact yet roomy enough for everyday essentials.",
                "price": 149.99,
                "images": json.dumps([
                    "https://picsum.photos/seed/leather-bag-1/600/800",
                    "https://picsum.photos/seed/leather-bag-2/600/800",
                    "https://picsum.photos/seed/leather-bag-3/600/800"
                ]),
                "sizes": json.dumps(["One Size"]),
                "colors": json.dumps(["Tan Leather", "Black", "Cognac"]),
                "stock": 14
            },
            {
                "category_slug": "accessories",
                "name": "Cashmere Ribbed Beanie",
                "description": "Knitted from 100% pure Mongolian cashmere for unmatched softness and warmth. Features a fold-over cuff and stretchy rib texture that fits all comfortably. A winter essential.",
                "price": 49.99,
                "images": json.dumps([
                    "https://picsum.photos/seed/cashmere-beanie-1/600/800",
                    "https://picsum.photos/seed/cashmere-beanie-2/600/800",
                    "https://picsum.photos/seed/cashmere-beanie-3/600/800"
                ]),
                "sizes": json.dumps(["One Size"]),
                "colors": json.dumps(["Charcoal", "Oatmeal", "Burgundy", "Navy"]),
                "stock": 35
            },
            {
                "category_slug": "accessories",
                "name": "Polarized Acetate Sunglasses",
                "description": "Classic square frame hand-cut from premium cellulose acetate with sturdy 5-barrel hinges. Equipped with category 3 polarized lenses offering 100% UV400 protection. Includes protective hard case.",
                "price": 89.99,
                "images": json.dumps([
                    "https://picsum.photos/seed/sunglasses-1/600/800",
                    "https://picsum.photos/seed/sunglasses-2/600/800",
                    "https://picsum.photos/seed/sunglasses-3/600/800"
                ]),
                "sizes": json.dumps(["One Size"]),
                "colors": json.dumps(["Tortoise Shell", "Black", "Honey Amber"]),
                "stock": 0
            },
            {
                "category_slug": "accessories",
                "name": "Wool Felt Fedora Hat",
                "description": "Molded from 100% Australian wool felt with a structured wide brim and teardrop crown. Trimmed with a tonal leather band and internal sweatband for comfortable fit.",
                "price": 69.99,
                "images": json.dumps([
                    "https://picsum.photos/seed/fedora-hat-1/600/800",
                    "https://picsum.photos/seed/fedora-hat-2/600/800",
                    "https://picsum.photos/seed/fedora-hat-3/600/800"
                ]),
                "sizes": json.dumps(["S/M", "L/XL"]),
                "colors": json.dumps(["Camel", "Black", "Olive"]),
                "stock": 12
            },

            # Footwear
            {
                "category_slug": "footwear",
                "name": "Leather Minimalist Sneakers",
                "description": "Clean low-top sneakers hand-crafted from smooth full-grain leather. Finished with durable Margom rubber soles, waxed cotton laces, and cushioned leather footbed. Sleek minimalism for versatile everyday styling.",
                "price": 139.99,
                "images": json.dumps([
                    "https://picsum.photos/seed/leather-sneakers-1/600/800",
                    "https://picsum.photos/seed/leather-sneakers-2/600/800",
                    "https://picsum.photos/seed/leather-sneakers-3/600/800"
                ]),
                "sizes": json.dumps(["7", "8", "9", "10", "11", "12"]),
                "colors": json.dumps(["White", "Black/White", "Off-White"]),
                "stock": 24
            },
            {
                "category_slug": "footwear",
                "name": "Chelsea Leather Boots",
                "description": "Timeless Chelsea boots made from supple calfskin leather with elastic side goring and pull tabs. Features Goodyear-welted rubber soles for longevity and water resistance.",
                "price": 189.99,
                "images": json.dumps([
                    "https://picsum.photos/seed/chelsea-boots-1/600/800",
                    "https://picsum.photos/seed/chelsea-boots-2/600/800",
                    "https://picsum.photos/seed/chelsea-boots-3/600/800"
                ]),
                "sizes": json.dumps(["7", "8", "9", "10", "11", "12"]),
                "colors": json.dumps(["Black", "Dark Brown", "Tan Suede"]),
                "stock": 18
            },
            {
                "category_slug": "footwear",
                "name": "Suede Loafers",
                "description": "Hand-stitched penny loafers crafted from soft Italian suede with leather linings. Built on flexible leather soles with a stacked heel. Ideal for refined spring and summer styling.",
                "price": 159.99,
                "images": json.dumps([
                    "https://picsum.photos/seed/suede-loafers-1/600/800",
                    "https://picsum.photos/seed/suede-loafers-2/600/800",
                    "https://picsum.photos/seed/suede-loafers-3/600/800"
                ]),
                "sizes": json.dumps(["7", "8", "9", "10", "11", "12"]),
                "colors": json.dumps(["Snuff Suede", "Navy Suede", "Chocolate"]),
                "stock": 9
            },
            {
                "category_slug": "footwear",
                "name": "Run-Performance Trainers",
                "description": "Engineered mesh upper providing high breathability and lightweight support. Features reactive foam midsole cushioning and high-traction rubber lug outsole for daily running or training.",
                "price": 119.99,
                "images": json.dumps([
                    "https://picsum.photos/seed/running-trainers-1/600/800",
                    "https://picsum.photos/seed/running-trainers-2/600/800",
                    "https://picsum.photos/seed/running-trainers-3/600/800"
                ]),
                "sizes": json.dumps(["7", "8", "9", "10", "11", "12"]),
                "colors": json.dumps(["Triple Black", "Grey/Neon", "White/Blue"]),
                "stock": 22
            }
        ]

        products_list = []
        for pdata in products_data:
            cat = categories[pdata["category_slug"]]
            product = Product(
                name=pdata["name"],
                description=pdata["description"],
                price=pdata["price"],
                category_id=cat.id,
                images=pdata["images"],
                sizes=pdata["sizes"],
                colors=pdata["colors"],
                stock=pdata["stock"]
            )
            db.session.add(product)
            products_list.append(product)

        db.session.flush()

        print("Seeding Reviews...")
        reviews_data = [
            (products_list[0], customer, 5, "Absolutely loved the fabric quality! Fits true to size and looks great dressed up or down."),
            (products_list[1], jane, 5, "The softest t-shirt I own. Holds its shape well after multiple washes."),
            (products_list[4], customer, 4, "Great chinos for work. Comfortable stretch and nice slim fit without being too tight."),
            (products_list[5], jane, 4, "Stiff at first as expected from raw denim, but breaking in nicely. Great red selvedge line."),
            (products_list[8], jane, 5, "The silk is so luxurious and soft. Beautiful drape, definitely worth every penny!"),
            (products_list[9], customer, 5, "Perfect basic tank. Material is thick enough so it isn't see-through at all."),
            (products_list[12], customer, 5, "Flattering fit and very elegant. Received so many compliments at the office."),
            (products_list[16], jane, 5, "Superior craftsmanship! Keeps the water off while maintaining a sleek classic silhouette."),
            (products_list[20], customer, 4, "Beautiful leather smell and finish. Fits my phone, wallet, and keys easily."),
            (products_list[21], jane, 5, "Super soft cashmere, keeps my head warm without itching."),
            (products_list[24], customer, 4, "Very clean aesthetic and surprisingly comfortable right out of the box. High quality leather."),
            (products_list[25], jane, 5, "Extremely well made boots. Goodyear welt ensures they will last for years.")
        ]

        for product, user, rating, comment in reviews_data:
            rev = Review(
                product_id=product.id,
                user_id=user.id,
                rating=rating,
                comment=comment
            )
            db.session.add(rev)

        print("Seeding Sample Order...")
        item1_price = products_list[0].price  # Oxford shirt $69.99
        item2_price = products_list[4].price  # Chinos $79.99 * 2
        item3_price = products_list[21].price # Beanie $49.99
        total_amount = round(item1_price + (item2_price * 2) + item3_price, 2)

        sample_order = Order(
            user_id=customer.id,
            email=customer.email,
            status="delivered",
            total=total_amount,
            shipping_method="Standard Shipping",
            shipping_address=json.dumps({
                "full_name": "Alex Morgan",
                "street": "123 Main Street, Apt 4B",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "country": "United States"
            })
        )
        db.session.add(sample_order)
        db.session.flush()

        order_items = [
            OrderItem(
                order_id=sample_order.id,
                product_id=products_list[0].id,
                product_name=products_list[0].name,
                product_price=item1_price,
                quantity=1,
                size="M",
                color="Light Blue"
            ),
            OrderItem(
                order_id=sample_order.id,
                product_id=products_list[4].id,
                product_name=products_list[4].name,
                product_price=item2_price,
                quantity=2,
                size="32",
                color="Navy"
            ),
            OrderItem(
                order_id=sample_order.id,
                product_id=products_list[21].id,
                product_name=products_list[21].name,
                product_price=item3_price,
                quantity=1,
                size="One Size",
                color="Charcoal"
            )
        ]
        db.session.add_all(order_items)

        db.session.commit()
        print('Seed data created successfully!')

if __name__ == '__main__':
    seed()
