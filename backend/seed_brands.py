#!/usr/bin/env python3
"""
Seed script: Populate 35 real US brands relevant to kids with products, offers, and problem categories.
Run: python seed_brands.py
"""
import asyncio
import os
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "leximaster_db")

def uid():
    return str(uuid.uuid4())

BRANDS = [
    # EDUCATION & LEARNING
    {
        "name": "LeapFrog", "website": "https://www.leapfrog.com",
        "description": "Interactive educational toys and tablets that make learning fun for children ages 2-8.",
        "problem_statement": "Children need engaging ways to learn reading, math, and critical thinking outside of school.",
        "problem_category": "education_tech",
        "products": [
            {"name": "LeapFrog LeapPad", "description": "Kid-safe learning tablet with 2000+ educational apps", "category": "education"},
            {"name": "LeapReader", "description": "Interactive reading and writing system that brings books to life", "category": "education"},
        ],
        "target_categories": ["education", "technology"],
        "bid_amount": 0.08, "budget_total": 500.0,
    },
    {
        "name": "National Geographic Kids", "website": "https://kids.nationalgeographic.com",
        "description": "Inspiring young explorers through science, nature, and world discovery content.",
        "problem_statement": "Kids are disconnected from the natural world and need inspiring ways to learn about science and geography.",
        "problem_category": "education_tech",
        "products": [
            {"name": "Nat Geo Kids Magazine", "description": "Monthly magazine with amazing animals, science experiments, and world facts", "category": "education"},
            {"name": "Nat Geo Explorer Kit", "description": "Hands-on science and exploration kits for young scientists", "category": "education"},
        ],
        "target_categories": ["education", "science"],
        "bid_amount": 0.07, "budget_total": 400.0,
    },
    {
        "name": "Scholastic", "website": "https://www.scholastic.com",
        "description": "The world's largest publisher of children's books, bringing stories to classrooms and homes.",
        "problem_statement": "Many children lack access to age-appropriate books that match their reading level and interests.",
        "problem_category": "reading_literacy",
        "products": [
            {"name": "Scholastic Book Clubs", "description": "Affordable book clubs delivering curated reading lists to schools", "category": "education"},
            {"name": "Scholastic Literacy Pro", "description": "Digital reading platform with thousands of leveled books", "category": "education"},
        ],
        "target_categories": ["education", "reading"],
        "bid_amount": 0.09, "budget_total": 600.0,
    },
    {
        "name": "ABCmouse", "website": "https://www.abcmouse.com",
        "description": "Award-winning early learning academy for children ages 2-8.",
        "problem_statement": "Young children need structured, fun digital learning programs to build school readiness.",
        "problem_category": "education_tech",
        "products": [
            {"name": "ABCmouse Learning Path", "description": "Step-by-step curriculum covering reading, math, science, and art", "category": "education"},
        ],
        "target_categories": ["education", "technology"],
        "bid_amount": 0.06, "budget_total": 450.0,
    },
    # HEALTHY FOOD & NUTRITION
    {
        "name": "Annie's Homegrown", "website": "https://www.annies.com",
        "description": "Organic and natural snacks and meals that families can feel good about.",
        "problem_statement": "Families struggle to find tasty, kid-approved foods that are also healthy and organic.",
        "problem_category": "healthy_food",
        "products": [
            {"name": "Annie's Organic Bunny Grahams", "description": "Crunchy organic snack crackers shaped like bunnies", "category": "food"},
            {"name": "Annie's Mac & Cheese", "description": "Organic macaroni and cheese made with real ingredients", "category": "food"},
        ],
        "target_categories": ["food", "health"],
        "bid_amount": 0.05, "budget_total": 350.0,
    },
    {
        "name": "Horizon Organic", "website": "https://www.horizonorganic.com",
        "description": "Organic dairy products from happy cows on family farms.",
        "problem_statement": "Kids need calcium and protein from dairy, but parents want organic options free from artificial growth hormones.",
        "problem_category": "healthy_food",
        "products": [
            {"name": "Horizon Organic Milk Boxes", "description": "Single-serve organic milk perfect for lunchboxes", "category": "food"},
            {"name": "Horizon Growing Years Milk", "description": "Specially formulated with DHA Omega-3 for growing kids", "category": "food"},
        ],
        "target_categories": ["food", "health"],
        "bid_amount": 0.06, "budget_total": 300.0,
    },
    {
        "name": "Clif Kid ZBar", "website": "https://www.clifbar.com/products/clif-kid",
        "description": "Organic energy bars made specifically for kids' active lives.",
        "problem_statement": "Active kids need nutritious, portable snacks that fuel their adventures without added sugars.",
        "problem_category": "healthy_food",
        "products": [
            {"name": "Clif Kid ZBar", "description": "Organic baked whole grain energy bar for kids", "category": "food"},
            {"name": "Clif Kid ZFruit", "description": "Organic fruit rope made from real fruit", "category": "food"},
        ],
        "target_categories": ["food", "sports"],
        "bid_amount": 0.05, "budget_total": 250.0,
    },
    # SPORTS & ACTIVE LIFESTYLE
    {
        "name": "Nike Kids", "website": "https://www.nike.com/kids",
        "description": "Athletic footwear and apparel designed to keep kids moving and confident.",
        "problem_statement": "Kids need comfortable, durable athletic gear that supports their active lifestyles and builds confidence in sports.",
        "problem_category": "sports_active",
        "products": [
            {"name": "Nike Star Runner", "description": "Lightweight running shoes designed for young athletes", "category": "sports"},
            {"name": "Nike Dri-FIT", "description": "Moisture-wicking athletic wear that keeps kids cool and dry", "category": "sports"},
        ],
        "target_categories": ["sports", "clothing"],
        "bid_amount": 0.12, "budget_total": 800.0,
    },
    {
        "name": "Adidas Kids", "website": "https://www.adidas.com/us/kids",
        "description": "Performance sportswear and sneakers for young athletes and everyday adventures.",
        "problem_statement": "Growing kids need versatile, high-quality athletic shoes that support their feet during sports and play.",
        "problem_category": "sports_active",
        "products": [
            {"name": "Adidas Ultraboost Kids", "description": "Comfortable running shoes with responsive cushioning for young runners", "category": "sports"},
            {"name": "Adidas Predator Soccer Cleats", "description": "Soccer cleats designed for young players to control the ball better", "category": "sports"},
        ],
        "target_categories": ["sports", "clothing"],
        "bid_amount": 0.11, "budget_total": 750.0,
    },
    {
        "name": "Schwinn", "website": "https://www.schwinnbikes.com",
        "description": "Bicycles and riding gear that get families outside and active together.",
        "problem_statement": "Kids spend too much time indoors; they need accessible outdoor activities that build fitness and independence.",
        "problem_category": "sports_active",
        "products": [
            {"name": "Schwinn SmartStart Bike", "description": "Kids' bikes with proportional design for easier learning", "category": "sports"},
            {"name": "Schwinn Kids Helmet", "description": "Colorful, safe helmets that kids actually want to wear", "category": "sports"},
        ],
        "target_categories": ["sports", "outdoor"],
        "bid_amount": 0.07, "budget_total": 400.0,
    },
    # ARTS & CREATIVITY
    {
        "name": "Crayola", "website": "https://www.crayola.com",
        "description": "Inspiring creativity in every child through colorful art supplies and experiences.",
        "problem_statement": "Children need accessible, high-quality art supplies to express themselves creatively and develop fine motor skills.",
        "problem_category": "arts_creativity",
        "products": [
            {"name": "Crayola Inspiration Art Case", "description": "140-piece art set with crayons, colored pencils, and markers", "category": "arts"},
            {"name": "Crayola Model Magic", "description": "Soft, moldable modeling compound that air-dries for sculpture projects", "category": "arts"},
        ],
        "target_categories": ["arts", "education"],
        "bid_amount": 0.08, "budget_total": 500.0,
    },
    {
        "name": "LEGO", "website": "https://www.lego.com",
        "description": "Building sets that develop creativity, problem-solving, and STEM skills through play.",
        "problem_statement": "Kids need hands-on activities that build spatial reasoning, engineering thinking, and creative problem-solving.",
        "problem_category": "arts_creativity",
        "products": [
            {"name": "LEGO Classic Creative Bricks", "description": "Open-ended building set for unlimited creative possibilities", "category": "toys"},
            {"name": "LEGO Education SPIKE", "description": "STEM robotics set that teaches coding through hands-on building", "category": "education"},
        ],
        "target_categories": ["education", "toys"],
        "bid_amount": 0.15, "budget_total": 1000.0,
    },
    {
        "name": "Melissa & Doug", "website": "https://www.melissaanddoug.com",
        "description": "Screen-free toys and activities that spark imagination and hands-on learning.",
        "problem_statement": "Children are over-exposed to screens; they need engaging, screen-free toys that develop real-world skills.",
        "problem_category": "arts_creativity",
        "products": [
            {"name": "Melissa & Doug Wooden Building Blocks", "description": "100-piece wooden block set for creative construction", "category": "toys"},
            {"name": "Melissa & Doug Art Easel", "description": "Double-sided art easel with chalkboard and whiteboard", "category": "arts"},
        ],
        "target_categories": ["toys", "arts"],
        "bid_amount": 0.07, "budget_total": 400.0,
    },
    # HEALTH & HYGIENE
    {
        "name": "Tom's of Maine Kids", "website": "https://www.tomsofmaine.com",
        "description": "Natural personal care products that are safe for kids and the environment.",
        "problem_statement": "Parents want toothpaste and hygiene products for kids that are natural, fluoride-safe, and taste good enough for kids to use willingly.",
        "problem_category": "health_hygiene",
        "products": [
            {"name": "Tom's Kids Fluoride Toothpaste", "description": "Natural fruit-flavored toothpaste that makes brushing fun", "category": "health"},
            {"name": "Tom's Wicked Cool Deodorant", "description": "Natural aluminum-free deodorant for tweens", "category": "health"},
        ],
        "target_categories": ["health"],
        "bid_amount": 0.05, "budget_total": 250.0,
    },
    {
        "name": "Band-Aid Brand", "website": "https://www.band-aid.com",
        "description": "Trusted wound care that gets kids back to playing faster.",
        "problem_statement": "Active kids get scrapes and cuts; they need bandages that stay on, heal properly, and come in fun designs.",
        "problem_category": "health_hygiene",
        "products": [
            {"name": "Band-Aid Flexible Fabric", "description": "Flexible bandages that move with active kids", "category": "health"},
            {"name": "Band-Aid Hydro Seal", "description": "Waterproof healing bandages for faster recovery", "category": "health"},
        ],
        "target_categories": ["health"],
        "bid_amount": 0.04, "budget_total": 200.0,
    },
    # TECHNOLOGY & CODING
    {
        "name": "Osmo", "website": "https://www.playosmo.com",
        "description": "AI-powered learning games that blend physical play with digital interaction.",
        "problem_statement": "Kids need technology that teaches rather than distracts, blending hands-on play with educational software.",
        "problem_category": "education_tech",
        "products": [
            {"name": "Osmo Genius Starter Kit", "description": "Hands-on learning system for math, spelling, and problem-solving", "category": "education"},
            {"name": "Osmo Coding Starter Kit", "description": "Physical coding blocks that teach programming logic through play", "category": "education"},
        ],
        "target_categories": ["education", "technology"],
        "bid_amount": 0.10, "budget_total": 550.0,
    },
    {
        "name": "Kano Computing", "website": "https://www.kano.me",
        "description": "Build-it-yourself computer kits that teach kids to code and create.",
        "problem_statement": "Kids consume technology but don't understand how it works; they need hands-on ways to learn coding and computer science.",
        "problem_category": "education_tech",
        "products": [
            {"name": "Kano PC", "description": "Build-your-own computer with step-by-step coding challenges", "category": "technology"},
            {"name": "Kano Pixel Kit", "description": "LED light board that teaches coding through art and games", "category": "technology"},
        ],
        "target_categories": ["technology", "education"],
        "bid_amount": 0.08, "budget_total": 400.0,
    },
    # OUTDOOR & NATURE
    {
        "name": "REI Kids", "website": "https://www.rei.com/c/kids",
        "description": "Outdoor gear and apparel that gets families exploring nature together.",
        "problem_statement": "Many kids lack outdoor experience; they need quality gear and inspiration to explore nature safely.",
        "problem_category": "outdoor_nature",
        "products": [
            {"name": "REI Co-op Kids Backpack", "description": "Kid-sized hiking backpack for day adventures", "category": "outdoor"},
            {"name": "REI Kids Rain Jacket", "description": "Waterproof, breathable jacket for outdoor adventures in any weather", "category": "outdoor"},
        ],
        "target_categories": ["outdoor", "sports"],
        "bid_amount": 0.07, "budget_total": 350.0,
    },
    {
        "name": "Hydro Flask Kids", "website": "https://www.hydroflask.com",
        "description": "Insulated water bottles that keep kids hydrated during school and play.",
        "problem_statement": "Kids don't drink enough water; they need appealing, durable water bottles that keep drinks cold all day.",
        "problem_category": "health_hygiene",
        "products": [
            {"name": "Hydro Flask Kids Wide Mouth", "description": "12oz insulated water bottle in fun colors for kids", "category": "outdoor"},
        ],
        "target_categories": ["health", "outdoor"],
        "bid_amount": 0.05, "budget_total": 200.0,
    },
    # READING & BOOKS
    {
        "name": "Epic! Kids Books", "website": "https://www.getepic.com",
        "description": "Digital library with 40,000+ books, audiobooks, and educational videos for kids.",
        "problem_statement": "Families need affordable access to a massive library of age-appropriate books to foster daily reading habits.",
        "problem_category": "reading_literacy",
        "products": [
            {"name": "Epic! Unlimited", "description": "Unlimited access to 40,000+ kids' books and audiobooks", "category": "education"},
        ],
        "target_categories": ["education", "reading"],
        "bid_amount": 0.08, "budget_total": 450.0,
    },
    {
        "name": "Audible Kids", "website": "https://www.audible.com/ep/kids",
        "description": "Audiobooks and original stories that bring reading to life through listening.",
        "problem_statement": "Some children struggle with traditional reading but thrive with audio content that builds listening comprehension and vocabulary.",
        "problem_category": "reading_literacy",
        "products": [
            {"name": "Audible Kids+", "description": "Thousands of kid-friendly audiobooks, podcasts, and Audible Originals", "category": "education"},
        ],
        "target_categories": ["education", "reading"],
        "bid_amount": 0.10, "budget_total": 600.0,
    },
    # FINANCIAL LITERACY
    {
        "name": "Greenlight", "website": "https://www.greenlight.com",
        "description": "Debit card and money app that teaches kids real-world financial skills.",
        "problem_statement": "Kids grow up without basic financial literacy; they need real tools to learn saving, budgeting, and smart spending.",
        "problem_category": "financial_literacy",
        "products": [
            {"name": "Greenlight Debit Card", "description": "Kid-safe debit card with parental controls and savings goals", "category": "finance"},
            {"name": "Greenlight Invest", "description": "Custodial investing that teaches kids about stocks and compound growth", "category": "finance"},
        ],
        "target_categories": ["finance", "education"],
        "bid_amount": 0.12, "budget_total": 700.0,
    },
    {
        "name": "BusyKid", "website": "https://busykid.com",
        "description": "Chore-based allowance app that teaches kids to earn, save, spend, and give.",
        "problem_statement": "Kids need to learn the connection between work and money through structured chore systems with real financial rewards.",
        "problem_category": "financial_literacy",
        "products": [
            {"name": "BusyKid App & Card", "description": "Chore tracking app with Visa prepaid card for kids' earnings", "category": "finance"},
        ],
        "target_categories": ["finance", "education"],
        "bid_amount": 0.08, "budget_total": 350.0,
    },
    # SCIENCE & STEM
    {
        "name": "littleBits", "website": "https://www.littlebits.com",
        "description": "Electronic building blocks that snap together to teach kids about circuits and engineering.",
        "problem_statement": "Kids need tangible ways to learn electronics and engineering that are safe and easy enough for beginners.",
        "problem_category": "stem_science",
        "products": [
            {"name": "littleBits Base Inventor Kit", "description": "16-piece electronics kit to build 12+ inventions", "category": "education"},
            {"name": "littleBits Space Rover", "description": "Build and code your own Mars rover", "category": "education"},
        ],
        "target_categories": ["education", "technology"],
        "bid_amount": 0.09, "budget_total": 450.0,
    },
    {
        "name": "Thames & Kosmos", "website": "https://www.thamesandkosmos.com",
        "description": "Award-winning science kits and experiments for curious young minds.",
        "problem_statement": "Science education needs hands-on experiments, not just textbooks; kids learn best by doing real science at home.",
        "problem_category": "stem_science",
        "products": [
            {"name": "Kids First Chemistry Set", "description": "Safe, fun chemistry experiments for ages 4+", "category": "education"},
            {"name": "Robotics Workshop", "description": "Build 10+ motorized robots with step-by-step instructions", "category": "education"},
        ],
        "target_categories": ["education", "science"],
        "bid_amount": 0.07, "budget_total": 350.0,
    },
    # CLOTHING & ESSENTIALS
    {
        "name": "Primary", "website": "https://www.primary.com",
        "description": "Simple, high-quality kids' clothing in every color — no logos, no slogans, just great basics.",
        "problem_statement": "Parents waste money on trendy, low-quality kids' clothes; they need durable, comfortable basics that last through growth spurts.",
        "problem_category": "clothing_essentials",
        "products": [
            {"name": "Primary Classic Tee", "description": "Super-soft organic cotton t-shirt in 20+ colors", "category": "clothing"},
            {"name": "Primary Joggers", "description": "Durable, comfortable pants for school and play", "category": "clothing"},
        ],
        "target_categories": ["clothing"],
        "bid_amount": 0.06, "budget_total": 300.0,
    },
    {
        "name": "L.L.Bean Kids", "website": "https://www.llbean.com/llbean/shop/506697",
        "description": "Rugged, outdoor-ready kids' clothing built to last with a legendary guarantee.",
        "problem_statement": "Kids are hard on clothes; families need durable gear that survives play, school, and outdoor adventures.",
        "problem_category": "clothing_essentials",
        "products": [
            {"name": "L.L.Bean Kids Backpack", "description": "Durable school backpack with lifetime guarantee", "category": "clothing"},
            {"name": "L.L.Bean Kids Bean Boots", "description": "Waterproof boots that keep kids dry in any weather", "category": "clothing"},
        ],
        "target_categories": ["clothing", "outdoor"],
        "bid_amount": 0.07, "budget_total": 400.0,
    },
    # MUSIC & MOVEMENT
    {
        "name": "Casio Mini Keyboards", "website": "https://www.casio.com",
        "description": "Affordable, beginner-friendly keyboards that introduce kids to the joy of music.",
        "problem_statement": "Music education is being cut from schools; kids need affordable instruments to discover their musical talents at home.",
        "problem_category": "music_movement",
        "products": [
            {"name": "Casio SA-76 Mini Keyboard", "description": "44-key mini keyboard with 100 tones perfect for beginners", "category": "music"},
        ],
        "target_categories": ["music", "education"],
        "bid_amount": 0.06, "budget_total": 300.0,
    },
    # SAFETY & WELL-BEING
    {
        "name": "Gabb Wireless", "website": "https://www.gabb.com",
        "description": "Kid-safe phones with no social media, no internet, just calls and texts.",
        "problem_statement": "Parents want their kids to have phones for safety but are worried about social media addiction and inappropriate content.",
        "problem_category": "safety_wellbeing",
        "products": [
            {"name": "Gabb Phone", "description": "Kid-safe smartphone with calls, texts, GPS — no social media or internet", "category": "technology"},
            {"name": "Gabb Watch", "description": "GPS-enabled smartwatch for younger kids with calling and safety features", "category": "technology"},
        ],
        "target_categories": ["technology", "safety"],
        "bid_amount": 0.10, "budget_total": 500.0,
    },
    # GARDENING & ENVIRONMENT
    {
        "name": "Kiwi Co", "website": "https://www.kiwico.com",
        "description": "Monthly STEAM project crates delivered to your door for hands-on learning.",
        "problem_statement": "Busy families need curated, age-appropriate STEAM projects that are ready to go without planning or shopping for supplies.",
        "problem_category": "stem_science",
        "products": [
            {"name": "KiwiCo Koala Crate", "description": "Monthly STEAM projects for ages 2-4 with all materials included", "category": "education"},
            {"name": "KiwiCo Kiwi Crate", "description": "Monthly science and art projects for ages 5-8", "category": "education"},
            {"name": "KiwiCo Tinker Crate", "description": "Engineering and design challenges for ages 9-16+", "category": "education"},
        ],
        "target_categories": ["education", "science"],
        "bid_amount": 0.11, "budget_total": 600.0,
    },
    # SLEEP & WELLNESS
    {
        "name": "Moshi Sleep", "website": "https://www.moshikids.com",
        "description": "Audio stories, music, and meditations designed to help kids fall asleep peacefully.",
        "problem_statement": "Many kids struggle with bedtime anxiety and trouble falling asleep; they need calming audio content designed for young minds.",
        "problem_category": "safety_wellbeing",
        "products": [
            {"name": "Moshi Sleep App", "description": "Calming bedtime stories, soundscapes, and guided meditations for kids", "category": "health"},
        ],
        "target_categories": ["health", "education"],
        "bid_amount": 0.06, "budget_total": 300.0,
    },
    # COOKING & LIFE SKILLS
    {
        "name": "Raddish Kids", "website": "https://www.raddishkids.com",
        "description": "Monthly cooking kits that teach kids culinary skills, math, and science through recipes.",
        "problem_statement": "Kids lack basic cooking skills; they need hands-on culinary education that teaches math, science, and independence.",
        "problem_category": "life_skills",
        "products": [
            {"name": "Raddish Cooking Kit", "description": "Monthly themed cooking kit with recipes, tools, and learning activities", "category": "education"},
        ],
        "target_categories": ["education", "food"],
        "bid_amount": 0.07, "budget_total": 350.0,
    },
    # TRANSPORTATION & MOBILITY
    {
        "name": "Razor Scooters", "website": "https://www.razor.com",
        "description": "Scooters, ride-ons, and outdoor toys that get kids moving and having fun outside.",
        "problem_statement": "Kids need fun, safe ways to be active outdoors that aren't organized sports — independent, unstructured outdoor play.",
        "problem_category": "sports_active",
        "products": [
            {"name": "Razor A Kick Scooter", "description": "Classic folding kick scooter for ages 5+", "category": "sports"},
            {"name": "Razor Hovertrax", "description": "Self-balancing hoverboard for kids 8+", "category": "sports"},
        ],
        "target_categories": ["sports", "outdoor"],
        "bid_amount": 0.08, "budget_total": 400.0,
    },
    # EYEWEAR & VISION
    {
        "name": "Warby Parker Kids", "website": "https://www.warbyparker.com/kids-glasses",
        "description": "Affordable, stylish eyeglasses for kids with free home try-on.",
        "problem_statement": "Kids with vision problems often avoid wearing glasses because they don't look cool; they need stylish, affordable options.",
        "problem_category": "health_hygiene",
        "products": [
            {"name": "Warby Parker Kids Glasses", "description": "Trendy, durable kids' eyeglasses starting at $95 with lenses", "category": "health"},
        ],
        "target_categories": ["health"],
        "bid_amount": 0.06, "budget_total": 300.0,
    },
]

OFFERS = [
    {"brand_name": "LeapFrog", "title": "20% Off LeapPad Tablets", "description": "Save 20% on any LeapPad learning tablet. Use code LEARN20.", "offer_type": "free", "external_link": "https://www.leapfrog.com/tablets"},
    {"brand_name": "Scholastic", "title": "Free Book with Every Order", "description": "Get a free bonus book with any Scholastic Book Club order this month!", "offer_type": "free", "external_link": "https://www.scholastic.com/bookclubs"},
    {"brand_name": "Annie's Homegrown", "title": "$2 Off Annie's Organic Snacks", "description": "Save $2 on any Annie's product at your local grocery store. Print coupon below.", "offer_type": "free", "external_link": "https://www.annies.com/coupons"},
    {"brand_name": "Nike Kids", "title": "Back to School Sale - 30% Off", "description": "30% off all Nike Kids footwear and apparel for back-to-school season.", "offer_type": "free", "external_link": "https://www.nike.com/kids-sale"},
    {"brand_name": "Crayola", "title": "Free Art Activity Downloads", "description": "Download free printable coloring pages and art activities from Crayola.", "offer_type": "free", "external_link": "https://www.crayola.com/free-coloring-pages"},
    {"brand_name": "LEGO", "title": "Double VIP Points This Weekend", "description": "Earn double VIP points on all LEGO Kids sets this weekend only.", "offer_type": "free", "external_link": "https://www.lego.com/vip"},
    {"brand_name": "Greenlight", "title": "First Month Free", "description": "Try Greenlight family banking free for 30 days. Teach your kids about money!", "offer_type": "free", "external_link": "https://www.greenlight.com/trial"},
    {"brand_name": "KiwiCo", "title": "50% Off First Crate", "description": "Get your first KiwiCo STEAM crate for half price. Hands-on learning delivered monthly!", "offer_type": "free", "external_link": "https://www.kiwico.com/promo"},
    {"brand_name": "Epic! Kids Books", "title": "Free 30-Day Trial", "description": "Unlimited access to 40,000+ kids' books free for 30 days.", "offer_type": "free", "external_link": "https://www.getepic.com/trial"},
    {"brand_name": "Gabb Wireless", "title": "$50 Off Gabb Phone", "description": "Save $50 on a kid-safe Gabb Phone. No social media, no internet — just peace of mind.", "offer_type": "free", "external_link": "https://www.gabb.com/promo"},
    {"brand_name": "Osmo", "title": "Free Shipping on Starter Kits", "description": "Free shipping on all Osmo Starter Kits. Learning meets play!", "offer_type": "free", "external_link": "https://www.playosmo.com/free-shipping"},
    {"brand_name": "Audible Kids", "title": "3 Months Free Audible Kids+", "description": "3 months free of Audible Kids+ with thousands of audiobooks for young listeners.", "offer_type": "free", "external_link": "https://www.audible.com/kids-trial"},
]


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    # Get admin user for created_by
    admin = await db.users.find_one({"role": "admin"}, {"_id": 0})
    admin_id = admin["id"] if admin else ""

    print("Seeding brands...")
    brand_map = {}
    for b_data in BRANDS:
        # Check if brand already exists
        existing = await db.brands.find_one({"name": b_data["name"]}, {"_id": 0})
        if existing:
            print(f"  [SKIP] {b_data['name']} already exists")
            brand_map[b_data["name"]] = existing["id"]
            continue

        brand_id = uid()
        brand_map[b_data["name"]] = brand_id
        products = [{"id": uid(), "name": p["name"], "description": p["description"], "category": p.get("category", "")} for p in b_data["products"]]
        brand_doc = {
            "id": brand_id,
            "name": b_data["name"],
            "logo_url": "",
            "website": b_data["website"],
            "description": b_data["description"],
            "problem_statement": b_data["problem_statement"],
            "problem_category": b_data["problem_category"],
            "bid_amount": b_data["bid_amount"],
            "products": products,
            "target_ages": [],  # All ages by default
            "target_categories": b_data["target_categories"],
            "target_regions": [],
            "target_languages": [],
            "budget_total": b_data["budget_total"],
            "budget_spent": 0.0,
            "cost_per_impression": b_data["bid_amount"],
            "is_active": True,
            "total_impressions": 0,
            "total_stories": 0,
            "rotation_count": 0,
            "onboarding_completed": True,
            "story_preview": "",
            "story_preview_generated_at": None,
            "created_by": admin_id,
            "created_date": datetime.now(timezone.utc).isoformat(),
        }
        await db.brands.insert_one(brand_doc)
        print(f"  [OK] {b_data['name']} ({b_data['problem_category']}, bid: ${b_data['bid_amount']})")

    print(f"\nSeeding {len(OFFERS)} brand offers...")
    for o_data in OFFERS:
        brand_id = brand_map.get(o_data["brand_name"], "")
        if not brand_id:
            print(f"  [SKIP] No brand found for {o_data['brand_name']}")
            continue
        existing = await db.brandoffers.find_one({"title": o_data["title"]}, {"_id": 0})
        if existing:
            print(f"  [SKIP] Offer '{o_data['title']}' already exists")
            continue
        offer_doc = {
            "id": uid(),
            "brand_id": brand_id,
            "brand_name": o_data["brand_name"],
            "title": o_data["title"],
            "description": o_data["description"],
            "offer_type": o_data["offer_type"],
            "price": 0.0,
            "external_link": o_data.get("external_link"),
            "internal_promo_code": None,
            "is_active": True,
            "target_all_users": True,
            "target_user_ids": [],
            "views": 0,
            "clicks": 0,
            "created_date": datetime.now(timezone.utc).isoformat(),
        }
        await db.brandoffers.insert_one(offer_doc)
        print(f"  [OK] Offer: {o_data['title']}")

    # Summary
    total_brands = await db.brands.count_documents({})
    total_offers = await db.brandoffers.count_documents({})
    print(f"\nDone! Total brands: {total_brands}, Total offers: {total_offers}")

    # List categories
    cats = set()
    async for b in db.brands.find({"problem_category": {"$ne": ""}}, {"problem_category": 1, "_id": 0}):
        cats.add(b["problem_category"])
    print(f"Problem categories: {sorted(cats)}")

    client.close()

if __name__ == "__main__":
    asyncio.run(main())
