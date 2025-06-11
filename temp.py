from faker import Faker
from random import randint, choice
from app import app,db,Service_Provider,Service

# Initialize the Faker instance
fake = Faker("en_IN")  # Generate Indian context data

# Generate and insert fake data
with app.app_context():
    service_provider_data = []
    for _ in range(20):  # Generating 20 fake records
        image = fake.image_url()
        alt = fake.text(max_nb_chars=20)
        title = fake.text(max_nb_chars=50)
        description = fake.text(max_nb_chars=200)
        section_id = fake.uuid4()

        service = Service(image=image, alt=alt, title=title, description=description, section_id=section_id)
        db.session.add(service)
    # Add the records to the session
    db.session.add_all(service_provider_data)

    # Commit the session to save the data in the database
    db.session.commit()

    print("Fake data added successfully!")

#  Run the script to add fake data 