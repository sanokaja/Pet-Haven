from faker import Faker
import random 
from datetime import datetime, timedelta, time
from app import db,app
from app import Booking,Sale,Sale_detail

fake = Faker()

def random_date(start, end):
    return start + timedelta(days=random.randint(0, int((end - start).days)))

def random_time():
    start_hour = random.choice([10, 11, 12, 13, 14, 15])
    return time(start_hour, 0)

def create_fake_bookings(num_bookings):
    start_date = datetime.strptime('2024-11-01', '%Y-%m-%d')
    end_date = datetime.strptime('2025-01-31', '%Y-%m-%d')
    with app.app_context():

        for _ in range(num_bookings):
            booking_date = random_date(start_date, end_date)
            booking_time = random_time()
            
            sale_detail = Sale_detail(
                sale_id=random.randint(1, 10),  # Assuming you have 10 sales
                breed_name=fake.random_element(elements=('Labrador', 'Poodle', 'Bulldog', 'Beagle', 'German Shepherd')),
                price=fake.random_number(digits=5, fix_len=True),
                dog_id=random.randint(1, 10)  # Assuming you have 10 dogs
            )
            db.session.add(sale_detail)
        db.session.commit()
# Create 10 fake bookings
create_fake_bookings(20)
