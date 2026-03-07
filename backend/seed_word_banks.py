"""
Seed word banks for LexiMaster
Run this script to populate the database with sample word banks
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path
import uuid

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]


SAMPLE_WORD_BANKS = [
    {
        "id": str(uuid.uuid4()),
        "name": "Space Exploration Fundamentals",
        "description": "Essential vocabulary for young space enthusiasts, covering planets, stars, and space missions",
        "category": "general",
        "specialty": "Space Science",
        "visibility": "global",
        "grade_range": {"min": "k", "max": "8"},
        "baseline_words": [
            {"word": "planet", "definition": "A large celestial body orbiting a star", "part_of_speech": "noun", "example_sentence": "Earth is the third planet from the Sun."},
            {"word": "star", "definition": "A glowing ball of gas in space", "part_of_speech": "noun", "example_sentence": "The Sun is our closest star."},
            {"word": "rocket", "definition": "A vehicle that travels to space", "part_of_speech": "noun", "example_sentence": "The rocket launched into orbit."},
            {"word": "astronaut", "definition": "A person who travels to space", "part_of_speech": "noun", "example_sentence": "The astronaut floated in zero gravity."},
            {"word": "orbit", "definition": "The path an object takes around another", "part_of_speech": "noun", "example_sentence": "The Moon is in orbit around Earth."},
            {"word": "moon", "definition": "A natural satellite orbiting a planet", "part_of_speech": "noun", "example_sentence": "The moon reflects sunlight at night."},
        ],
        "target_words": [
            {"word": "gravity", "definition": "The force that pulls objects together", "part_of_speech": "noun", "example_sentence": "Gravity keeps us on the ground."},
            {"word": "telescope", "definition": "An instrument to see distant objects", "part_of_speech": "noun", "example_sentence": "We used a telescope to see Mars."},
            {"word": "atmosphere", "definition": "The layer of gases around a planet", "part_of_speech": "noun", "example_sentence": "Earth's atmosphere protects us from radiation."},
        ],
        "stretch_words": [
            {"word": "constellation", "definition": "A group of stars forming a pattern", "part_of_speech": "noun", "example_sentence": "Orion is a famous constellation."},
        ],
        "total_tokens": 10,
        "price": 0,
        "owner_id": "system",
        "purchase_count": 0,
        "rating": 4.8
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Dinosaur Discovery",
        "description": "Learn about prehistoric creatures, fossils, and paleontology",
        "category": "general",
        "specialty": "Paleontology",
        "visibility": "global",
        "grade_range": {"min": "pre-k", "max": "6"},
        "baseline_words": [
            {"word": "dinosaur", "definition": "A prehistoric reptile", "part_of_speech": "noun", "example_sentence": "The Tyrannosaurus rex was a fierce dinosaur."},
            {"word": "fossil", "definition": "Preserved remains of ancient life", "part_of_speech": "noun", "example_sentence": "Scientists found a dinosaur fossil."},
            {"word": "extinct", "definition": "No longer existing", "part_of_speech": "adjective", "example_sentence": "Dinosaurs are extinct animals."},
            {"word": "carnivore", "definition": "An animal that eats meat", "part_of_speech": "noun", "example_sentence": "The T-rex was a carnivore."},
            {"word": "herbivore", "definition": "An animal that eats plants", "part_of_speech": "noun", "example_sentence": "The Brontosaurus was a herbivore."},
            {"word": "prehistoric", "definition": "Before written history", "part_of_speech": "adjective", "example_sentence": "Dinosaurs lived in prehistoric times."},
        ],
        "target_words": [
            {"word": "paleontologist", "definition": "A scientist who studies fossils", "part_of_speech": "noun", "example_sentence": "The paleontologist discovered a new species."},
            {"word": "excavate", "definition": "To dig up carefully", "part_of_speech": "verb", "example_sentence": "They excavated the fossil from the rock."},
            {"word": "predator", "definition": "An animal that hunts others", "part_of_speech": "noun", "example_sentence": "The velociraptor was a skilled predator."},
        ],
        "stretch_words": [
            {"word": "Mesozoic", "definition": "The era when dinosaurs lived", "part_of_speech": "noun", "example_sentence": "The Mesozoic era lasted millions of years."},
        ],
        "total_tokens": 10,
        "price": 0,
        "owner_id": "system",
        "purchase_count": 0,
        "rating": 4.9
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Aviation Essentials",
        "description": "Professional vocabulary for aspiring pilots and aviation enthusiasts",
        "category": "professional",
        "specialty": "Aviation",
        "visibility": "marketplace",
        "grade_range": {"min": "1-12", "max": "adult"},
        "baseline_words": [
            {"word": "aircraft", "definition": "A vehicle designed for air travel", "part_of_speech": "noun", "example_sentence": "The aircraft took off smoothly."},
            {"word": "altitude", "definition": "Height above sea level", "part_of_speech": "noun", "example_sentence": "The plane reached an altitude of 30,000 feet."},
            {"word": "runway", "definition": "A strip for aircraft takeoff and landing", "part_of_speech": "noun", "example_sentence": "The jet taxied down the runway."},
            {"word": "cockpit", "definition": "The pilot's control area", "part_of_speech": "noun", "example_sentence": "The captain sat in the cockpit."},
            {"word": "navigation", "definition": "Finding direction during travel", "part_of_speech": "noun", "example_sentence": "GPS helps with navigation."},
            {"word": "turbulence", "definition": "Irregular air movement", "part_of_speech": "noun", "example_sentence": "We experienced turbulence during the flight."},
        ],
        "target_words": [
            {"word": "aerodynamics", "definition": "The study of air movement", "part_of_speech": "noun", "example_sentence": "Good aerodynamics improve fuel efficiency."},
            {"word": "fuselage", "definition": "The main body of an aircraft", "part_of_speech": "noun", "example_sentence": "Passengers sit inside the fuselage."},
            {"word": "avionics", "definition": "Electronic systems in aircraft", "part_of_speech": "noun", "example_sentence": "Modern avionics include autopilot systems."},
        ],
        "stretch_words": [
            {"word": "transponder", "definition": "A device that transmits aircraft information", "part_of_speech": "noun", "example_sentence": "The transponder sends altitude data to controllers."},
        ],
        "total_tokens": 10,
        "price": 499,  # $4.99
        "owner_id": "system",
        "purchase_count": 0,
        "rating": 5.0
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Medical Terminology Basics",
        "description": "Foundational medical vocabulary for students interested in healthcare",
        "category": "professional",
        "specialty": "Medicine",
        "visibility": "marketplace",
        "grade_range": {"min": "1-12", "max": "adult"},
        "baseline_words": [
            {"word": "diagnosis", "definition": "Identifying a disease", "part_of_speech": "noun", "example_sentence": "The doctor made a diagnosis."},
            {"word": "symptom", "definition": "A sign of illness", "part_of_speech": "noun", "example_sentence": "Fever is a common symptom."},
            {"word": "treatment", "definition": "Medical care to cure illness", "part_of_speech": "noun", "example_sentence": "The treatment was successful."},
            {"word": "prescription", "definition": "A written order for medicine", "part_of_speech": "noun", "example_sentence": "The pharmacist filled the prescription."},
            {"word": "anatomy", "definition": "The study of body structure", "part_of_speech": "noun", "example_sentence": "We learned about human anatomy."},
            {"word": "vital", "definition": "Essential for life", "part_of_speech": "adjective", "example_sentence": "The heart is a vital organ."},
        ],
        "target_words": [
            {"word": "pathology", "definition": "The study of disease", "part_of_speech": "noun", "example_sentence": "Pathology helps understand illness."},
            {"word": "prognosis", "definition": "Expected outcome of disease", "part_of_speech": "noun", "example_sentence": "The prognosis was optimistic."},
            {"word": "chronic", "definition": "Long-lasting condition", "part_of_speech": "adjective", "example_sentence": "Diabetes is a chronic disease."},
        ],
        "stretch_words": [
            {"word": "epidemiology", "definition": "Study of disease patterns", "part_of_speech": "noun", "example_sentence": "Epidemiology tracks disease spread."},
        ],
        "total_tokens": 10,
        "price": 699,  # $6.99
        "owner_id": "system",
        "purchase_count": 0,
        "rating": 4.7
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Robotics & AI Fundamentals",
        "description": "Modern technology vocabulary for future engineers and programmers",
        "category": "academic",
        "specialty": "Technology",
        "visibility": "global",
        "grade_range": {"min": "1-12", "max": "college"},
        "baseline_words": [
            {"word": "robot", "definition": "A programmable machine", "part_of_speech": "noun", "example_sentence": "The robot performed tasks automatically."},
            {"word": "sensor", "definition": "A device that detects changes", "part_of_speech": "noun", "example_sentence": "The sensor detected motion."},
            {"word": "program", "definition": "Instructions for a computer", "part_of_speech": "noun", "example_sentence": "She wrote a program to solve the problem."},
            {"word": "artificial", "definition": "Made by humans, not natural", "part_of_speech": "adjective", "example_sentence": "Artificial intelligence powers chatbots."},
            {"word": "data", "definition": "Information processed by computers", "part_of_speech": "noun", "example_sentence": "The computer analyzed the data."},
            {"word": "algorithm", "definition": "A step-by-step problem-solving method", "part_of_speech": "noun", "example_sentence": "The algorithm sorted the numbers."},
        ],
        "target_words": [
            {"word": "automation", "definition": "Using machines to do tasks", "part_of_speech": "noun", "example_sentence": "Automation increased factory efficiency."},
            {"word": "processor", "definition": "The brain of a computer", "part_of_speech": "noun", "example_sentence": "The processor executes instructions."},
            {"word": "interface", "definition": "Connection between systems", "part_of_speech": "noun", "example_sentence": "The user interface was intuitive."},
        ],
        "stretch_words": [
            {"word": "neural network", "definition": "AI system modeled on the brain", "part_of_speech": "noun", "example_sentence": "Neural networks recognize patterns."},
        ],
        "total_tokens": 10,
        "price": 0,
        "owner_id": "system",
        "purchase_count": 0,
        "rating": 4.9
    }
]


async def seed_word_banks():
    """Seed the database with sample word banks"""
    print("Starting word bank seeding...")
    
    # Clear existing word banks (optional - comment out if you want to keep existing)
    # await db.word_banks.delete_many({"owner_id": "system"})
    
    # Check if word banks already exist
    existing_count = await db.word_banks.count_documents({"owner_id": "system"})
    if existing_count > 0:
        print(f"Found {existing_count} existing system word banks. Skipping seed.")
        return
    
    # Insert word banks
    for bank in SAMPLE_WORD_BANKS:
        await db.word_banks.insert_one(bank)
        print(f"✓ Created word bank: {bank['name']}")
    
    print(f"\n✅ Successfully seeded {len(SAMPLE_WORD_BANKS)} word banks!")
    
    # Print summary
    print("\n📊 Word Bank Summary:")
    print(f"  Global (Free): {sum(1 for b in SAMPLE_WORD_BANKS if b['visibility'] == 'global')}")
    print(f"  Marketplace (Paid): {sum(1 for b in SAMPLE_WORD_BANKS if b['visibility'] == 'marketplace')}")
    

if __name__ == "__main__":
    asyncio.run(seed_word_banks())
    client.close()
