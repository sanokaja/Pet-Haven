import re
import uuid 
import time
from flask import send_from_directory, abort
from flask import Flask, flash, redirect, render_template, request, jsonify, session, url_for, session as flask_session
from flask import abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_migrate import Migrate
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import random
import sqlite3
import os
import sendgrid
from bcrypt import checkpw
from flask import Flask, render_template, request, redirect, flash, url_for, session, send_from_directory
#import sendgrid
#from sendgrid.helpers.mail import Mail, Email, To, Content
from datetime import date
#from PIL import Image
from werkzeug.security import generate_password_hash
from sqlalchemy import MetaData
from sqlalchemy import and_
from sqlalchemy import func
from sqlalchemy import MetaData
import plotly.express as px
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
import plotly.io as pio
from sqlalchemy.sql import text

from sqlalchemy.exc import OperationalError
from flask import send_from_directory, abort
from werkzeug.utils import safe_join 
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = MetaData(naming_convention=convention)
app = Flask(__name__)
app.secret_key = 'pethaven'

# Database Configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'static/db/Petheaven.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app,metadata=metadata)
migrate = Migrate(app, db)

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_DEFAULT_SENDER'] = 'noreply@gmail.com'
notif_mail = Mail(app)
mail=Mail(app)


# Database Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    # Add service provider specific fields
    service_type = db.Column(db.String(50))
    location = db.Column(db.String(255))
    hourly_rate = db.Column(db.Float)
    certifications = db.Column(db.Text)
    experience = db.Column(db.Integer)
    id_proof_path = db.Column(db.String(255), nullable=True)
    qualification_path = db.Column(db.String(255), nullable=True)
    certification_path = db.Column(db.String(255), nullable=True)

class Pet(db.Model):
    __tablename__ = 'pet'

    pet_id = db.Column(db.Integer, primary_key=True)
    breed = db.Column(db.String(50), nullable=False)
    age_months = db.Column(db.Integer, nullable=False)
    health_records = db.Column(db.String(200))
    price = db.Column(db.Numeric, nullable=False)
    availability_status = db.Column(db.String(20))
    achivement = db.Column(db.String(200))
    image = db.Column(db.String(255))
    description = db.Column(db.String(200))

class Cart(db.Model):
    __tablename__ = 'cart'

    id =db.Column(db.Integer, primary_key=True)
    # customer_id = db.Column(db.Integer,db.ForeignKey('customer.id'))
    pet_id =db.Column(db.Integer, nullable=False)

class AdminCart(db.Model):
    __tablename__ = 'admin_cart'

    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, nullable=False)

class Sale(db.Model):
    __tablename__ = 'sales'

    sale_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    buyer_name = db.Column(db.String(100), nullable=False)
    sale_date = db.Column(db.DateTime, nullable=False)
    sale_price = db.Column(db.Numeric, nullable=False)
    payment_method = db.Column(db.String, nullable=False, default="Cash On Delivery")
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)

    def __init__(self, buyer_name, sale_price, payment_method, invoice_number):
        self.buyer_name = buyer_name
        self.sale_price = sale_price
        self.payment_method = payment_method
        self.invoice_number = invoice_number
        self.sale_date = datetime.now()

class Sale_detail(db.Model):
    __tablename__= 'sale_detail'

    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sale_id = db.Column(db.Integer, nullable=False)
    breed_name = db.Column(db.String(50), nullable=False) 
    price =	db.Column(db.Numeric, nullable=False)
    dog_id = db.Column(db.Integer, nullable=False)	

    def __init__(self, sale_id, breed_name, price, dog_id):
        self.sale_id = sale_id
        self.breed_name = breed_name
        self.price = price
        self.dog_id = dog_id

class Dog_sales(db.Model):
    __tablename__= 'Dog_sales'

    breed_id = db.Column(db.Integer, primary_key=True)
    breed = db.Column(db.String(50), nullable=False) 
    quantity = db.Column(db.Integer, nullable=False, default = 0)
    price = db.Column(db.Integer, nullable=False)	

events_list = []
# Registration model
def generate_dog_id():
    last_dog = Registration.query.order_by(Registration.id.desc()).first()
    if last_dog:
        last_number = int(last_dog.id.replace("Dog", ""))
        next_number = last_number + 1
    else:
        next_number = 101  # Start from 101
    return f"Dog{next_number}"

class Registration(db.Model):
    id = db.Column(db.String(10), primary_key=True, default=generate_dog_id)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    competition_name = db.Column(db.String(100), nullable=False)
    dog_name = db.Column(db.String(100), nullable=False)
    breed = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    achievements = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Pending')  # Added status
    
    event = db.relationship('Event', backref='registrations')

class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    address = db.Column(db.Text, nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    
    competitions_registered = db.Column(db.Text, nullable=True)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    venue = db.Column(db.String(150), nullable=False)
    image = db.Column(db.String(200), nullable=False)  # Store the image path
    def is_active(self):
        return self.date >= date.today()
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(50), nullable=False)
    payment_status = db.Column(db.String(20), nullable=False, default='Pending')

    customer = db.relationship('Customer', backref=db.backref('payments', lazy=True))

class CartEvent(db.Model):
    __tablename__ = 'cart_event'
    id = db.Column(db.Integer, primary_key=True)
    registration_id = db.Column(db.String, db.ForeignKey('registration.id'), nullable=False)
    price = db.Column(db.Float, db.ForeignKey('event.price'), nullable=False)
    
    registration = db.relationship('Registration', backref='cart_items',lazy='joined')
    event = db.relationship('Event', backref='cart_items')


# ! """---------------------------------------------------------------------------------------------------------"""
#! TEAM 3 CODE STARTS HERE
class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(255), nullable=False)
    alt = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    section_id = db.Column(db.String(100), nullable=False, unique=True)

    def __init__(self, image, alt, title, description, section_id):
        self.image = image
        self.alt = alt
        self.title = title
        self.description = description
        self.section_id = section_id

class Service_Provider(db.Model):
    __tablename__ = 'service_provider'
    service_provider_id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(255),nullable = False)
    # expertise = db.Column(db.String(255),nullable = False)
    experience = db.Column(db.Integer,nullable = False)
    availability = db.Column(db.Boolean,nullable = False,default = True)
    service_provided_id = db.Column(db.Integer,db.ForeignKey('services.id'),nullable = False)
    description = db.Column(db.String(255))
    cost = db.Column(db.Integer)
    location = db.Column(db.String(255))
    def __init__(self, name, experience, availability, service_provided_id, description=None, cost=None, location=None):
        self.name = name
        self.experience = experience
        self.availability = availability
        self.service_provided_id = service_provided_id
        self.description = description
        self.cost = cost
        self.location = location


class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('service_provider.service_provider_id'), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    booking_time = db.Column(db.Time, nullable=False)
    # pet_id 
    
    def __init__(self, name, email, phone, service_id, provider_id, booking_date, booking_time):
        self.name = name
        self.email = email
        self.phone = phone
        self.service_id = service_id
        self.provider_id = provider_id
        self.booking_date = booking_date
        self.booking_time = booking_time

class Slot_Booked():

    __tablename__ = "slot_booked"
    id = db.Column(db.Integer,primary_key = True)
    service_provider_id = db.Column(db.Integer,db.ForeignKey('service_provider.service_provider_id'))
    start_time = db.Column(db.Time,nullable = True)
    end_time = db.Column(db.Time,nullable = True)
    booking_date = db.Column(db.Date,nullable = True)
    customer_id = db.Column(db.Integer,db.ForeignKey('customer.id'))

    def __init__(self,service_provider_id,start_time,end_time,booking_date,customer_id):
        self.service_provider_id = service_provider_id
        self.start_time = start_time
        self.end_time = end_time
        self.booking_date = booking_date
        self.customer_id = customer_id
        
class Final_Order():
    __tablename__ = "final_orders"
    id = db.Column(db.Integer,primary_key = True,autoincrement = True)
    customer_id = db.Column(db.Integer,db.ForeignKey('customer.id'))
    slot_id = db.Column(db.Integer,db.ForeignKey("slot_booked.id"))

    def __init__(self,customer_id,slot_id):
        self.customer_id = customer_id
        self.slot_id = slot_id
        

class ShippingDetails(db.Model):
    __tablename__ = 'shipping_details'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    shipping_id = db.Column(db.Integer, db.ForeignKey('shipping_details.id'), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')

class EditRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(200))  # Hashed password
    service_type = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    certifications = db.Column(db.Text, nullable=False)
    experience = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Final_Cart(db.Model):
    __tablename__ = 'final_cart'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    user_id = db.Column(db.Integer,nullable=False)
    service_provider_id = db.Column(db.Integer, db.ForeignKey('service_provider.service_provider_id'), nullable=False)
    booking_date = db.Column(db.Date, nullable=True)
    booking_time = db.Column(db.Time, nullable=True)

    def __init__(self, user_id , service_provider_id, booking_date=None, booking_time=None):
        self.user_id = user_id
        self.service_provider_id = service_provider_id
        self.booking_date = booking_date
        self.booking_time = booking_time

    
@app.route('/get-service-providers', methods=['GET'])
def get_service_providers():
    try:
        service_providers = User.query.filter_by(role='service-provider').all()
        providers_list = [
            {
                'id': sp.id,  # Ensure ID is included
                'fullname': sp.fullname,
                'email': sp.email,
                'service_type': sp.service_type,
                'location': sp.location,
                'hourly_rate': sp.hourly_rate,
                'certifications': sp.certifications,
                'experience': sp.experience,
                'id_proof_path': sp.id_proof_path,
                'qualification_path': sp.qualification_path,
            }
            for sp in service_providers
        ]
        return jsonify({'status': 'success', 'data': providers_list})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/admin-dashboard')
def admin_page():  # Rename function to avoid conflict
    service_providers = User.query.filter_by(role='service-provider').all()
    return render_template('admin_dashboard.html', service_providers=service_providers)
# Temporary OTP Store
otp_store = {}

# Configurations
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Get the base directory of the Flask app
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads') 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'jpg', 'jpeg', 'png'}


# Ensure uploads directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Function to check allowed extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# Routes
@app.teardown_appcontext
def shutdown_session(exception=None):
    try:
        db.session.remove()
    except OperationalError:
        pass
@app.route('/uploads/<path:filename>')  # Use <path:filename> to allow spaces
def uploaded_file(filename):
    try:
        safe_path = safe_join(app.config['UPLOAD_FOLDER'], filename)

        # Check if the file exists
        if not os.path.exists(safe_path):
            return "File Not Found", 404

        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        print(f"Error: {e}")
        return abort(500)

@app.route('/show-users')
def display_users():
    show_users()
    return "User data has been printed in the console."

@app.route('/delete_submission/<int:index>', methods=['POST'])
def delete_submission(index):
    # Debugging: Check if the function is being called
    print(f"Deleting submission at index: {index}")

    # Get the list of submissions from the session
    submissions = session.get('submissions', [])
    print(f"Current submissions: {submissions}")  # Debugging: Check submissions

    # Ensure the index is valid
    if 0 <= index < len(submissions):
        # Remove the submission from the list
        submissions.pop(index)
        # Debugging: Print updated submissions
        print(f"Updated submissions: {submissions}")

        # Update the session with the modified submissions list
        session['submissions'] = submissions
    else:
        print("Invalid index")

    # Redirect back to the admin dashboard
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_fromservice_providertable/<int:user_id>', methods=['DELETE'])
def delete_fromservice_providertable(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        db.session.delete(user)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'User deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/delete_service_provider/<int:id>', methods=['GET'])
def delete_service_provider(id):
    # Assuming `service_providers` is your data source (list or DB)
    global service_providers
    provider = next((p for p in service_providers if p['id'] == id), None)
    
    if provider:
        service_providers = [p for p in service_providers if p['id'] != id]  # Remove the provider
        return jsonify({'message': 'Service provider deleted successfully'})
    else:
        return jsonify({'error': 'Service provider not found'}), 404
    

@app.before_request
def ensure_fresh_session():
    # Clear session if the request is the first one after starting the app
    if not session.get('initialized'):
        session.clear()
        session['initialized'] = True



@app.route('/')
def home():
    # If no active session, render the customer landing page by default
    if not session.get('role'):
        return render_template('landing_page.html', user_name=None)

    # Check if the user is logged in as a service provider
    if session.get('role') == 'service-provider':
        if 'user_id' in session:
            return redirect(url_for('service_provider_landing'))
        else:
            session.clear()
            return redirect(url_for('login'))

    # Check if the user is logged in as a customer
    if session.get('role') == 'customer':
        user_name = session.get('fullname', 'Guest')
        return render_template('landing_page.html', user_name=user_name)

    # Fallback for unexpected roles
    session.clear()
    return render_template('landing_page.html', user_name=None)
   


   
@app.route('/service-provider-landing')
def service_provider_landing():
    if 'fullname' in session and session['role'] == 'service-provider':
        user_name = session['fullname']
        return render_template('service_provider_landing.html', user_name=user_name)
    else:
        flash('Please log in first')
        return redirect(url_for('login'))

@app.route('/service_provider')
def service_provider():
    return render_template('service_provider.html')

    
@app.route('/logout')
def logout():
    # Get the role of the user before clearing the session
    user_role = session.get('role')
    
    # Debug: Print session content before clearing
    print(f"Session before logout: {session}")
    
    # Clear the session to log out the user
    session.clear()

    # Debug: Print session content after clearing
    print(f"Session after logout: {session}")
    
    # Flash message for logout success
    flash('You have been logged out successfully.')

    # Redirect based on the role of the user
    if user_role == 'customer':
        return redirect(url_for('home'))  # Redirect customer to the landing page
    elif user_role == 'service-provider':
        return redirect(url_for('service_provider_landing'))  # Redirect service provider to their landing page
    else:
        return redirect(url_for('login'))  # If no role is found, redirect to login page

  
@app.route('/apply')
def apply():
    return render_template('apply.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    submissions = session.get('submissions', [])
    index_submissions = session.get('index_submissions', [])
    return render_template('admin_dashboard.html', submissions=submissions, index_submissions=index_submissions)

@app.route('/admin_landing')
def admin_landing():
    return render_template('admin_landing.html')

@app.route('/submit_application', methods=['POST'])
def submit_application():
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    service_requested = request.form.get('service_requested')

    # Handle file uploads
    id_proof = None
    qualification = None
    certification = None

    # Save files with unique filenames
    if 'id_proof' in request.files:
        file = request.files['id_proof']
        if file and allowed_file(file.filename):
            id_proof =save_file_default(file)

    if 'qualification' in request.files:
        file = request.files['qualification']
        if file and allowed_file(file.filename):
            qualification = save_file_default(file)
            


    if 'certification' in request.files:
        file = request.files['certification']
        if file and allowed_file(file.filename):
            certification = save_file_default(file)

    # Store the submission data in session
    submissions = session.get('submissions', [])
    submissions.append({
    "full_name": full_name,
    "email": email,
    "phone": phone,
    "service_requested": service_requested,
    "id_proof": id_proof,
    "qualification": qualification,
    "certification": certification,
    "experience": request.form.get("experience", "N/A")
})

    session['submissions'] = submissions  # Store updated submissions in session

    # Redirect to home page after submission
    return redirect(url_for('home'))

def save_file_default(file):
    """Save files to the default 'uploads/' folder."""
    if file:
        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return filename
    return None



@app.route('/upload-documents')
def upload_documents():
    return render_template('upload_doc.html')

@app.route('/home')
def home_page():
    return render_template('landing_page.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('index.html')  # Render the register page for GET requests

    # Handle POST request logic for registration
    data = request.form

    # Validate common fields
    required_fields = ['fullname', 'email', 'password', 'role']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    if data['password'] != data.get('confirm_password', ''):
        return jsonify({"error": "Passwords do not match"}), 400

    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, data['email']):
        return jsonify({"error": "Invalid email address. Please use a valid format like name@example.com."}), 400

    # Role-based handling
    role = data.get('role')

    if role == 'service-provider':
        # Validate service provider fields
        service_fields = ['service_type', 'location', 'hourly_rate', 'experience']
        for field in service_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required for service providers"}), 400

        # File handling
        def save_file(file):
            if file and allowed_file(file.filename):
                filename = f"{uuid.uuid4()}_{file.filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # Save file in the uploads folder
                return filename  # Store only the filename in the database
            return None

        id_proof_path = save_file(request.files.get('id-proof'))
        qualification_path = save_file(request.files.get('qualification'))

        if not id_proof_path or not qualification_path:
            return jsonify({"error": "All required documents must be uploaded"}), 400

        # Create a new service provider user
        new_user = User(
            fullname=data['fullname'],
            email=data['email'],
            password=data['password'],
            role=data['role'],
            service_type=data['service_type'],
            location=data['location'],
            hourly_rate=float(data['hourly_rate']),
            certifications=data.get('certifications', ''),
            experience=int(data['experience']),
            id_proof_path=id_proof_path,
            qualification_path=qualification_path
        )
    elif role == 'customer':
        # Create a new customer user
        new_user = User(
            fullname=data['fullname'],
            email=data['email'],
            password=data['password'],
            role=data['role']
        )
    else:
        return jsonify({"error": "Invalid role"}), 400

    # Save the user to the database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Registration successful", "role": role, "fullname": data['fullname']}), 201



    otp = "123456"  # Simulated OTP

    # Prepare response data
    response_data = {
        "fullname": data['fullname'],
        "email": data['email'],
        "role": data['role']
    }

    # Response with OTP
    return jsonify({
        "message": "Registration successful. OTP sent to your registered contact.",
        "otp": otp,
        "data": response_data
    })

# Route to Send OTP for Registration
@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data['email']
    session['temp_email'] = email

    if User.query.filter_by(email=email).first():
        return jsonify({'status': 'error', 'message': 'Email already registered!'}), 400

    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp

    try:
        msg = Message('Your PetCare OTP', sender=app.config['MAIL_USERNAME'], recipients=[email])
        msg.body = f"Your OTP for registration is: {otp}"
        mail.send(msg)
        return jsonify({'status': 'success', 'message': 'OTP sent to your email.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to send OTP: {str(e)}'}), 500

# Route to Verify OTP and Register User
@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.form  
    email = session.get('temp_email')
    entered_otp = data['otp']
    fullname = data['fullname']
    role = data['role']

    if not email or email not in otp_store:
        return jsonify({'status': 'error', 'message': 'No OTP sent for this email.'}), 400

    if otp_store[email] != entered_otp:
        return jsonify({'status': 'error', 'message': 'Invalid OTP.'}), 400
    
    print("Received Files:", request.files)  # DEBUGGING

    # File handling
    def save_file(file):
        if file and allowed_file(file.filename):
            filename = f"{uuid.uuid4()}_{file.filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                file.save(file_path)
                print(f"File saved at: {file_path}")  # DEBUGGING
                return filename
            except Exception as e:
                print(f"File save error: {e}")  # DEBUGGING
                return None
        print("Invalid file or not provided")  # DEBUGGING
        return None

    id_proof_path = save_file(request.files.get('id-proof'))
    qualification_path = save_file(request.files.get('qualification'))

    print(f"ID Proof Path: {id_proof_path}, Qualification Path: {qualification_path}")  # DEBUGGING

    try:
        if role == 'customer':
            new_user = User(fullname=fullname, email=email, password=data['password'], role=role)
        elif role == 'service-provider':
            new_user = User(
                fullname=fullname,
                email=email,
                password=data['password'],
                role=role,
                service_type=data['service_type'],
                location=data['location'],
                hourly_rate=float(data['hourly_rate']),
                certifications=data['certifications'],
                experience=int(data['experience']),
                id_proof_path=id_proof_path,
                qualification_path=qualification_path
            )
        
        db.session.add(new_user)
        db.session.commit()
        del otp_store[email]
        session.pop('temp_email', None)

        if role == 'customer':
            return jsonify({'status': 'success', 'message': 'Registration successful!'})
        elif role == 'service-provider':
            return jsonify({'status': 'success', 'message': 'Documents uploaded. Wait for admin approval.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Registration failed: {str(e)}'}), 500

@app.route('/send-registration-email', methods=['POST'])
def send_registration_email():
    data = request.get_json()
    fullname = data['fullname']
    email = data['email']

    try:
        msg = Message(
            'Registration Successful - PetCare',
            sender=app.config['MAIL_USERNAME'],
            recipients=[email],
        )
        msg.body = f"Hello {fullname},\n\nYour registration with PetCare was successful. Welcome to our platform!\n\nThank you,\nPetCare Team"
        mail.send(msg)
        return jsonify({'status': 'success', 'message': 'Registration email sent.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to send email: {str(e)}'}), 500


# Admin Route to Approve Users
@app.route('/admin/approve-user/<int:user_id>', methods=['POST'])
def approve_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found!'}), 404

    try:
        msg = Message('Registration Approved - PetCare', sender=app.config['MAIL_USERNAME'], recipients=[user.email])
        msg.body = f"Hello {user.fullname},\n\nYour registration with PetCare has been approved. You can now log in to access our services.\n\nThank you,\nPetCare Team"
        mail.send(msg)

        return jsonify({'status': 'success', 'message': 'User approved and notified via email.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to send approval email: {str(e)}'}), 500

# Admin Route to Deny Users
@app.route('/admin/deny-user/<int:user_id>', methods=['POST'])
def deny_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found!'}), 404

    try:
        msg = Message('Registration Denied - PetCare', sender=app.config['MAIL_USERNAME'], recipients=[user.email])
        msg.body = f"Hello {user.fullname},\n\nWe regret to inform you that your registration with PetCare has been denied. If you believe this is an error, please contact our support team.\n\nThank you,\nPetCare Team"
        mail.send(msg)

        db.session.delete(user)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'User denied and notified via email.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to send denial email: {str(e)}'}), 500
    # Configure upload folder and allowed extensions


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def upload_form():
    return render_template('upload_form.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        files = {
            "id-proof": request.files.get('id-proof'),
            "qualification": request.files.get('qualification'),
            "Certifications": request.files.get('Certifications'),
        }
         
        paths={}
        errors = []
        for field, file in files.items():
            if field != "Certifications" and not file:  # Mandatory fields check
                errors.append(f"{field.replace('-', ' ').title()} is required.")
                continue

            if file and allowed_file(file.filename):
                filename = f"{field}_{file.filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                paths[f"{field.replace('-', '_')}_path"] = filepath
            elif file:
                errors.append(f"Invalid file format for {field.replace('-', ' ').title()}.")

        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('upload_form'))
        
        email = session.get('temp_email')  # Ensure the email is stored in the session
        if not email:
            flash('Error: No email associated with the session.', 'error')
            return redirect(url_for('upload_form'))
        
        
        user = User.query.filter_by(email=email).first()
        if user:
            user.id_proof_path = paths.get('id_proof_path')
            user.qualification_path = paths.get('qualification_path')
            user.certification_path = paths.get('certification_path')
            db.session.commit()
            flash('Documents uploaded successfully and saved to your profile!', 'success')
        else:
            flash('Error: User not found in the database.', 'error')
        
        return redirect(url_for('upload_form'))


# Other Routes (Login, Password Reset, etc.) remain unchanged


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('index.html')  # Render the login page for GET request

    # Handle the POST request (when login form is submitted)
    data = request.get_json()
    if not data.get('email') or not data.get('password'):
        return jsonify({'status': 'error', 'message': 'Email and password are required!'}), 400

    email = data['email'].strip().lower()
    password = data['password']
    role = data.get('role')

    user = User.query.filter_by(email=email, role=role).first()

    if user and user.password == password:
        # Store user information in session
        session['user_id'] = user.id
        session['fullname'] = user.fullname
        session['role'] = user.role

        # Redirect based on role after login
        if role == "customer":
            return jsonify({'status': 'success', 'redirect_url': '/'})  # Redirect to customer landing page
        elif role == "service-provider":
            return jsonify({'status': 'success', 'redirect_url': '/service-provider-landing'})  # Redirect to service provider landing page
    else:
        return jsonify({'status': 'error', 'message': 'Invalid email or password!'}), 401


@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data['email']
    new_password = data['new_password']

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found!'}), 400

    user.password = new_password
    db.session.commit()

    del otp_store[email]
    return jsonify({'status': 'success', 'message': 'Password reset successful!'})

# New email configuration for accept/reject notifications
app.config['NOTIF_MAIL_SERVER'] = 'smtp.example.com'  # Replace with your email server
app.config['NOTIF_MAIL_PORT'] = 587
app.config['NOTIF_MAIL_USE_TLS'] = True
app.config['NOTIF_MAIL_USERNAME'] = ''  # Replace with notification email
app.config['NOTIF_MAIL_PASSWORD'] = ''          # Replace with notification email password

# Initialize a separate Mail instance
notif_mail = Mail()
notif_mail.init_app(app)

def generate_password(length=8):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))

@app.route('/send_notification_email', methods=['POST'])
def send_notification_email():
    data = request.json
    email = data['email']
    action = data['action']
    password = data.get('password', None)  # Get password if provided (for accepted requests)
    user = User.query.filter_by(email=email).first()
    if user:
        user.password = password  # Store hashed password
        db.session.commit()
    else:
        return jsonify({"error": "User not found"}), 404
    subject = "Application Status Notification"
    
    if action == "accept":
        body = f"""Dear {data['full_name']},

Your application for the service '{data['service_requested']}' has been accepted.
Your username is your email: {email}
Your password is: {password}

Thank you!
"""
    elif action == "reject":
        body = f"""Dear {data['full_name']},

We regret to inform you that your application for the service '{data['service_requested']}' has been rejected.

Thank you!
"""
    
    try:
        msg = Message(subject, sender=app.config['NOTIF_MAIL_USERNAME'], recipients=[email])
        msg.body = body
        notif_mail.send(msg)
        return jsonify({"message": "Notification email sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to send email: {str(e)}"}), 500

    
    
# Query all users from the database
def show_users():
    with db.app.app_context():  # Create an application context
        users = User.query.all()
        if users:
            print("User Data in the Database:")
            for user in users:
                print(f"ID: {user.id}, Fullname: {user.fullname}, Email: {user.email}, Role: {user.role}")
                if user.role == 'service-provider':
                    print(f"Service Type: {user.service_type}, Location: {user.location}, Hourly Rate: {user.hourly_rate}, Certifications: {user.certifications}, Experience: {user.experience}, IdProof: {user.id_proof_path}, Qualifiaction: {user.qualification_path}, CertificationPath: {user.certification_path}")
        else:
            print("No user data found in the database.")

# Function to handle filtering logic
from sqlalchemy import func

def build_filter_query(breed, price_filter, age_filter):
    query = db.session.query(Pet)

    # ✅ Case-insensitive breed filtering
    if breed and breed.strip():
        query = query.filter(func.lower(Pet.breed) == breed.strip().lower())  

    # ✅ Price Filtering (Same as Before)
    if price_filter:
        if price_filter == "low":
            query = query.filter(Pet.price < 6000)
        elif price_filter == "medium":
            query = query.filter(Pet.price.between(6000, 10000))
        elif price_filter == "high":
            query = query.filter(Pet.price.between(10000, 15000))
        elif price_filter == "very high":  
            query = query.filter(Pet.price > 15000)

    # ✅ Age Filtering (Same as Before)
    if age_filter:
        if age_filter == "Puppy":
            query = query.filter(Pet.age_months <= 12)
        elif age_filter == "Young":
            query = query.filter(and_(Pet.age_months > 12, Pet.age_months <= 36))
        elif age_filter == "Adult":
            query = query.filter(Pet.age_months > 36)

    return query


@app.route('/cannine_home', methods=['GET'])
def cannine_home():
    role = request.args.get('role', default='customer')
    breed_filter = request.args.get('breed')
    price_filter = request.args.get('price')
    age_filter = request.args.get('age')

    unique_breeds = db.session.query(func.lower(Pet.breed)).distinct().all()
    breed_options = sorted(set(breed[0].capitalize() for breed in unique_breeds))

    price_ranges = [
        ("low", "Below ₹6000"),
        ("medium", "₹6000 - ₹10000"),
        ("high", "₹10000 - ₹15000"),
        ("very_high", "Above ₹15000")
    ]

    dogs_query = build_filter_query(breed_filter, price_filter, age_filter)
    dogs = dogs_query.all()

    return render_template(
        "index_cannine.html",
        dogs=dogs,
        breed_options=breed_options,
        price_ranges=price_ranges,
        role=role
    )


def get_cart_data():
    cart_items = db.session.query(Cart).all()
    cart_details = []
    for item in cart_items:
        pet = db.session.query(Pet).filter_by(pet_id=item.pet_id).first()
        if pet:
            cart_details.append({
                'id': item.id,
                'pet_id': pet.pet_id,
                'name': pet.breed,
                'price': float(pet.price),
                'total': float(pet.price) ,
                'image': pet.image
            })

    subtotal = sum(item['total'] for item in cart_details)
    shipping = 500 if subtotal > 0 else 0
    gst = subtotal * 0.05
    sgst = subtotal * 0.05
    total = subtotal + shipping + gst + sgst

    return {
        'cart_details': cart_details,
        'subtotal': subtotal,
        'shipping': shipping,
        'gst': gst,
        'sgst': sgst,
        'total': total
    }

# Customer Cart Routes
@app.route('/cart', methods=['GET'])
def view_cart():
    # ! This is Team 2 Cart Data 
    cart_data_2 = get_cart_data()
    # cart_items = Cart.query.all()
    # cart_items = Final_Cart.query.all()
    # trainers = []

    # for item in cart_items:
    #     trainer = Service_Provider.query.get(item.service_provider_id)
    #     if trainer:
    #         trainers.append(trainer)
    #! This is Team 3 Cart Data
    cart_items = Final_Cart.query.all()
    cart_data_3 = []
    for item in cart_items:
        trainer = Service_Provider.query.get(item.service_provider_id)
        if trainer:
            d = {
                'id': item.id,
                'name': trainer.name,
                'service_provider_id': item.service_provider_id,
                'booking_time': item.booking_time,
                "booking_date": item.booking_date,
                'cost': trainer.cost
            }
            cart_data_3.append(d)
    print(cart_data_3)
    #! This is Team 4 Cart Data 
    # cart_data_4 = Registration.query.all()
    # cart_data_4_Total = sum(item.event.price if item.event else 0 for item in cart_data_4)
    cart_data_4 = CartEvent.query.all() 
    cart_data_4_info = []
    for item in cart_data_4:
        event = Registration.query.get(item.registration_id)
        if event:
            d = {
                'id': item.id,
                'name': event.competition_name,
                'registration_id': item.registration_id,
                'cost': item.price
            }
            cart_data_4_info.append(d)
    cost = cart_data_2['subtotal']
    cost+= sum(item['cost'] for item in cart_data_4_info)
    for i in range(len(cart_data_3)):
        cost += cart_data_3[i]['cost']

    gst = int(cost * 0.05)
    sgst = gst // 2

    total = cost + gst + sgst
    return render_template(
        'cart.html',
        cart_data_2=cart_data_2['cart_details'],
        subtotal=cost,
        shipping=500,
        gst=gst,
        sgst=sgst,
        cart_data_3 = cart_data_3,
        cart_data_4 = cart_data_4_info,
        total = total
    )


@app.route('/add_to_cart/<int:pet_id>', methods=['POST'])
def add_to_cart(pet_id):
    try:
        pet =db.session.query(Pet).filter_by(pet_id=pet_id).first()
        if not pet:
            return "Pet not found", 404

        if pet.availability_status == 'sold':
            flash(f"{pet.breed} is no longer available for purchase.", "warning")
            return redirect(url_for('cannine_home'))

        cart_item =db.session.query(Cart).filter_by(pet_id=pet_id).first()
        if cart_item:
            flash(f"{pet.breed} is already in your cart!", "info")
            return redirect(url_for('cannine_home'))
        
        # Add new item to cart
        new_cart_item = Cart(pet_id=pet_id)
        db.session.add(new_cart_item)
        db.session.commit()
       
        flash(f"{pet.breed} has been added to your cart!", "success")
        return redirect(url_for('view_cart'))

    except Exception as e:
        print(f"Error adding to customer cart: {e}")
        return "Error adding item to cart", 500
    
@app.route('/delete_from_cart/<int:cart_item_id>', methods=['GET'])
def delete_from_cart(cart_item_id):
    cart_item = db.session.query(Cart).filter_by(id=cart_item_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
    return redirect(url_for('view_cart'))
    
@app.route('/policy', methods=['GET'])
def policy():
    return render_template("policy.html")

@app.route('/admin', methods=['GET'])
def admin():
    breed_filter = request.args.get('breed')
    price_filter = request.args.get('price')  # ✅ Matches HTML dropdown name
    age_filter = request.args.get('age')

    unique_breeds = db.session.query(func.lower(Pet.breed)).distinct().all()
    breed_options = sorted(set(breed[0].capitalize() for breed in unique_breeds))

    dogs_query = build_filter_query(breed_filter, price_filter, age_filter)
    dogs = dogs_query.all()

    return render_template(
        "admin.html",
        dogs=dogs,
        breed_options=breed_options,
        breed=breed_filter,
        price=price_filter,  # ✅ Pass price filter to HTML
        age=age_filter
    )



@app.route('/edit_dog/<int:pet_id>', methods=['POST', 'GET'])
def edit_dog(pet_id):
    pet = db.session.query(Pet).filter_by(pet_id=pet_id).first()
    if not pet:
        flash("Pet not found", "error")
        return redirect(url_for('admin'))

    if request.method == 'POST':
        changes_made = False
        fields = {
            'breed': request.form.get('breed', pet.breed),
            'price': float(request.form.get('price', pet.price)),
            'age_months': int(request.form.get('age', pet.age_months)),
            'health_records': request.form.get('Health_Record', pet.health_records),
            'availability_status': request.form.get('Availability', pet.availability_status),
            'description': request.form.get('description', pet.description),
            'achivement': request.form.get('achivement', pet.achivement),
        }

        # Check and apply changes
        for field, value in fields.items():
            if getattr(pet, field) != value:
                setattr(pet, field, value)
                changes_made = True

        if changes_made:
            try:
                db.session.commit()
                flash(f"Details for {pet.breed} updated successfully!", "success")
                return redirect(url_for('admin'))
            except Exception as e:
                db.session.rollback()
                flash(f"Error in editing {pet.breed}", "error")

    return render_template('edit_dog.html',pet=pet)

# Delete Dog (Admin)
@app.route('/delete_dog/<int:pet_id>', methods=['POST'])
def delete_dog(pet_id):
    try:
        pet = db.session.query(Pet).filter_by(pet_id=pet_id).first()
        if not pet:
            flash("Pet not found", "error")
            return redirect(url_for('admin'))

        if pet.image:
            image_path = os.path.join(os.path.dirname(__file__), 'static', 'images', pet.image)
            if os.path.isfile(image_path):
                os.remove(image_path)

        db.session.delete(pet)
        db.session.commit()
        flash(f"{pet.breed} has been deleted successfully!", "success")

    except Exception as e:
        db.session.rollback()
        flash("Error in deleting pet", "error")

    return redirect(url_for('admin'))


@app.route('/add_dog', methods=['GET', 'POST'])
def add_dog():
    if request.method == 'POST':
        try:
            image = request.files['image']

            UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images')
            app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

            if not image:
                flash("Error in adding image", "error")
                return redirect(request.url)

                
            if image:
                filename = secure_filename(image.filename)
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                print(f"Trying to save to: {save_path}")
                image.save(save_path)
                print(f"File saved successfully to {save_path}")
                
            breed = request.form.get('breed')
            age = request.form.get('age_months')
            health_records = request.form.get('Health_record')
            price = request.form.get('price')
            achivement = request.form.get('achiviements')
            
            # Create new pet
            new_pet = Pet(
                breed=breed,
                age_months=int(age),
                health_records=health_records,
                price=float(price),
                availability_status='Available',
                achivement=achivement,
                image=filename,
                description=f"A {breed} ({age} months old) with health status: '{health_records or 'No records'}' and achievements: '{achivement or 'None'}'."
            )
            
            db.session.add(new_pet)
            db.session.commit()
            
            flash(f"Dog {breed} added successfully!", "success")
            return redirect(url_for('admin'))
            
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            db.session.rollback()
            flash("Error in adding image", "error")
            return redirect(request.url)
            
    return render_template('add_dog.html')


# Admin Cart Routes


@app.route('/admin_policy', methods=['GET', 'POST'])
def admin_policy():
    return render_template('admin_policy.html')

def determine_cart_type():
    """
    Check which type of cart has items to determine if this is an admin or customer purchase
    Returns: 'admin' if items in admin cart, 'customer' if items in customer cart
    """
    admin_items = db.session.query(AdminCart).first()
    if admin_items:
        return 'admin'
    return 'customer'



@app.route('/shipping_details', methods=['GET', 'POST'])
def shipping_details():
    cart_type = determine_cart_type()

    if request.method == 'POST':
        flask_session['shipping_data'] = {
            'first_name': request.form.get('first_name'),
            'middle_name': request.form.get('middle_name'),
            'last_name': request.form.get('last_name'),
            'email': request.form.get('email'),
            'contact': request.form.get('contact'),
            'address': request.form.get('address'),
            'zip_code': request.form.get('zip_code'),
            'state': request.form.get('state'),
            'cart_type': cart_type  # Store cart type in session
        }
        return redirect(url_for('payment'))

    return render_template('shipping.html')

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    shipping_data = flask_session.get('shipping_data', {})
    cart_type = shipping_data.get('cart_type')

    if request.method == 'POST':
        payment_option = request.form.get('payment_option')
        flask_session['payment_option'] = payment_option
        return redirect(url_for('success'))

    return render_template('payment.html', **shipping_data)

# @app.route('/success')
# def success():
#     # Fixed typo in session key (removed space)
#     shipping_data = flask_session.get('shipping_data', {})
#     payment_option = flask_session.get('payment_option')
#     cart_type = shipping_data.get('cart_type', 'customer')
    
#     # Get cart data based on cart type
#     if cart_type == 'admin':
#         cart_data = get_admin_cart_data()
#         cart_table = AdminCart
#     else:
#         cart_data = get_cart_data()
#         cart_table = Cart

#     current_date = datetime.today().strftime('%Y-%m-%d')
#     expected_delivery_date = (datetime.today() + timedelta(days=5)).strftime('%Y-%m-%d')

#     template_data = {
#         **shipping_data,
#         'payment_option': payment_option,
#         'current_date': current_date,
#         'expected_delivery_date': expected_delivery_date,
#         'role': cart_type,  # Add role to template data
#         **cart_data
#     }
    
#     sale = Sale(
#         buyer_name=f"{shipping_data.get('first_name', '')} {shipping_data.get('last_name', '')}",
#         sale_date=datetime.now(),
#         sale_price=cart_data['total'],
#         payment_method=payment_option,
#         invoice_number=str(datetime.now().timestamp()).replace('.', '')
#     )
#     db.session.add(sale)
#     db.session.commit()
    
#     for cart_detail in cart_data['cart_details']:
#         sale_detail = Sale_detail(
#         sale_id=sale.sale_id,
#         breed_name=cart_detail['name'],
#         price=cart_detail['price'],
#         dog_id=cart_detail['pet_id']
#         )
#         db.session.add(sale_detail)

#     db.session.commit()

#     for cart_detail in cart_data['cart_details']:
#         dog_sales = db.session.query(Dog_sales).filter_by(breed=cart_detail['name']).first()
#         if not dog_sales:
#          dog_sales = Dog_sales(
#             breed=cart_detail['name'],
#             quantity=1,
#             price=cart_detail['price']
#          )
#          db.session.add(dog_sales)
#         else:
#          dog_sales.quantity += 1  # Increment quantity


#     db.session.commit()
    
#       # Update pet availability
#     for cart_detail in cart_data['cart_details']:
#         pet = db.session.query(Pet).filter_by(pet_id=cart_detail['pet_id']).first()
#         if pet:
#             pet.availability_status = 'sold'


#     # Clear the appropriate cart
#     db.session.query(cart_table).delete()
#     db.session.commit()

#     invoice_number = sale.invoice_number

   

#     pet_details = "\n".join([f"""
#         Pet: {item['name']}
#         Price: ₹{item['price']}
#         Quantity: {item.get('quantity', 1)}"""
#         for item in cart_data['cart_details']
#     ])

#     try:
#         msg = Message('Order Confirmation - PetCare', 
#                       sender=app.config['MAIL_USERNAME'], 
#                       recipients=[shipping_data['email']])
#         msg.body = f"""
#         Hello {shipping_data['first_name']},

#         Thank you for your purchase!
#         Here are your order details:

#         Order Date: {current_date}
#         Expected Delivery Date: {expected_delivery_date}

#         Order Details:

#         Invoice Number: {invoice_number}
#         Payment Method: {payment_option}
        
#         {pet_details}

#         Total: ₹{cart_data['total']}
        
#         We will notify you once your order has been shipped.

#         Thank you for choosing PetHaven!
#         """
#         mail.send(msg)
#         print("Order confirmation email sent successfully.")

#     except Exception as e:
#         print(f"Error sending email: {e}")

#     return render_template('success.html', **template_data)
            
@app.route('/competition', methods=['GET'])
def competition_page():
    events = Event.query.all()  # Assuming Event is your database model
    today = date.today()

    for event in events:
        event_date = event.date
        event.is_active = event_date >= today  # Mark events as active or inactive

    return render_template('competition_page.html', events=events)

@app.route('/register_competition', methods=['GET', 'POST'])
def register_competition():
    # Fetch the events from the database
    events = Event.query.all()

    # Loop over events and update the 'is_active' status
    today = date.today()
    for event in events:
        event_date = event.date
        event.is_active = event_date >= today

    # Check for POST request (form submission)
    if request.method == 'POST':
        competition_id = request.form.get('competition-name')  # Retrieve event ID
        dog_name = request.form.get('dog-name')
        breed = request.form.get('breed')
        age = request.form.get('age')
        achievements = request.form.get('achievements')

        # Find the selected event by its ID
        event = Event.query.filter_by(id=competition_id).first()

        if event:
            # Save the registration
            new_registration = Registration(
                # id=generate_dog_id(),
                event_id=event.id,  # Use the event's ID
                competition_name=event.name,  # Use event name from the found event
                dog_name=dog_name,
                breed=breed,
                age=age,
                achievements=achievements,
                status='Please complete payment process'  # Initially set as pending
            )

            db.session.add(new_registration)
            db.session.commit()

            flash("Successfully registered for the competition!", "regis")
            return redirect('/register_competition')
        else:
            flash("Invalid competition selected. Please try again.", "danger")

    # Return the registration page with event data
    return render_template('registration.html', events=events)




@app.route('/my-events')
def my_events():
    today = date.today()
    events = Event.query.all()
    registrations = Registration.query.all()
    carts = Cart.query.all()

    # Safely check if registration.event exists
    for registration in registrations:
        if registration.event:  # Ensure the event exists
            event_date = registration.event.date
            registration.event.is_active = event_date >= today
        else:
            registration.event = None  # Handle missing event reference

    return render_template('my_events.html', registrations=registrations, events=events, carts=carts)


@app.route('/edit/<string:id>', methods=['GET', 'POST'])
def edit_registration(id):
    registration = Registration.query.get_or_404(id)
    if request.method == 'POST':
        registration.competition_name = request.form.get('competition-name')
        registration.dog_name = request.form.get('dog-name')
        registration.breed = request.form.get('breed')
        registration.age = request.form.get('age')
        registration.achievements = request.form.get('achievements')

        db.session.commit()
        flash("Registration updated successfully!", "my_events")
        return redirect('/my-events')

    return render_template('edit_registration.html', registration=registration)

@app.route('/delete/<string:id>', methods=['GET'])
def delete_registration(id):
    registration = Registration.query.get_or_404(id)
    db.session.delete(registration)
    db.session.commit()
    flash("Registration deleted successfully!", "my_events")
    return redirect('/my-events')

@app.route('/admin_events', methods=['GET'])
def admin_events():
    events = Event.query.all()
    today = date.today()
    for event in events:
        event.is_active = event.date >= today 
    return render_template('admin_events.html', events=events)

@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        # Get form data
        event_name = request.form.get('event-name')
        event_description = request.form.get('event-description')
        event_price = request.form.get('event-price')
        event_date = request.form.get('event-date')
        event_venue = request.form.get('event-venue')
        
        # Handle file upload
        event_image = request.files.get('event-image')
        
        if not event_image:
            flash('Event image is required!', 'danger')
            return redirect(request.url)
        
        # Choose a dynamic directory for uploads (e.g., 'uploads/')
        upload_directory = os.path.join(app.root_path, 'uploads')
        if not os.path.exists(upload_directory):
            os.makedirs(upload_directory)
        
        # Save the image to the dynamic directory
        image_filename = event_image.filename
        image_path = os.path.join(upload_directory, image_filename)
        image_path = image_path.replace(os.sep, '/')
        
        try:
            event_image.save(image_path)
        except Exception as e:
            flash(f"Error saving image: {e}", 'danger')
            return redirect(request.url)
        
        # Ensure that the other fields are not empty
        if not event_name or not event_description or not event_price or not event_date or not event_venue:
            flash('All fields are required!', 'danger')
            return redirect(request.url)
        
        # Create new event object and add it to the database
        try:
            new_event = Event(
                name=event_name,
                description=event_description,
                price=float(event_price),
                date=datetime.strptime(event_date, '%Y-%m-%d'),
                venue=event_venue,
                image=image_path  # Store the correct path to the image
            )
            
            # Add the event to the database
            db.session.add(new_event)
            db.session.commit()
            send_email_to_all_customers(event_name, event_date, event_venue)
            flash('Event added successfully!', 'Admin')
            return redirect(url_for('admin_events'))
        
        except Exception as e:
            flash(f"Error adding event: {e}", 'danger')

    return render_template('add_event.html')
def send_email_to_all_customers(event_name, event_date, event_venue):
    # Fetch all customers from the Customer table
    customers = Customer.query.all()

    for customer in customers:
        # Send email to each customer
        send_event_registration_email(
            customer_name=customer.first_name,
            customer_email=customer.email,
            event_name=event_name,
            event_date=event_date,
            event_venue=event_venue
        )

def send_event_registration_email(customer_name, customer_email, event_name, event_date, event_venue):
    # Compose the email body
    email_body = f"""
    Dear {customer_name},

    We are excited to announce a new event: {event_name}!

    Event Details:
    Event Name: {event_name}
    Date: {event_date}
    Venue: {event_venue}

    We encourage you to register for this event at the earliest. Don't miss out on this wonderful opportunity!

    Best regards,
    Pet Haven Team
    """

    # Send the email
    try:
        msg = Message(
            subject="New Event Announcement: Register Now!",
            recipients=[customer_email],
            body=email_body
        )
        notif_mail.send(msg)
        print(f"Email sent to {customer_name} ({customer_email})")
    except Exception as e:
        print(f"Error sending email to {customer_name}: {e}")

@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    if request.method == 'POST':
        # Get form data
        event_name = request.form.get('event-name')
        event_description = request.form.get('event-description')
        event_price = request.form.get('event-price')
        event_date = request.form.get('event-date')
        event_venue = request.form.get('event-venue')
        
        # Handle file upload
        event_image = request.files.get('event-image')
        
        if event_image:
            # Handle the image if it is updated
            upload_directory = os.path.join(app.root_path, 'uploads')
            if not os.path.exists(upload_directory):
                os.makedirs(upload_directory)
            
            image_filename = event_image.filename
            image_path = os.path.join(upload_directory, image_filename)
            image_path = image_path.replace(os.sep, '/')
            
            try:
                event_image.save(image_path)
            except Exception as e:
                flash(f"Error saving image: {e}", 'danger')
                return redirect(request.url)
            
            event.image = image_path  # Update image path
        
        # Update other fields
        event.name = event_name
        event.description = event_description
        event.price = float(event_price)
        event.date = datetime.strptime(event_date, '%Y-%m-%d')
        event.venue = event_venue
        
        try:
            # Commit changes to the database
            db.session.commit()
            flash('Event updated successfully!', 'Admin')
            return redirect(url_for('admin_events'))
        
        except Exception as e:
            flash(f"Error updating event: {e}", 'danger')
    
    return render_template('Admin_edit_event.html', event=event)
@app.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    try:
        # Optionally, you can delete the image file as well (ensure the file is removed from the server)
        if event.image:
            image_path = os.path.join(app.root_path, event.image)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        # Delete the event from the database
        db.session.delete(event)
        db.session.commit()
        flash('Event deleted successfully!', 'Admin')
        return redirect(url_for('admin_events'))
    
    except Exception as e:
        flash(f"Error deleting event: {e}", 'danger')
        return redirect(url_for('admin_events'))

@app.route('/cart_event')
def cart_event():
    registrations = Registration.query.all()
    cart_entries = CartEvent.query.all()
    events=Event.query.all()

    total_price = sum(entry.price for entry in cart_entries)
    
    return render_template('cart_event.html', cart_entries=cart_entries, total_price=total_price,registrations=registrations,events=events)

    
@app.route('/add_item_to_cart', methods=['POST'])
def add_item_to_cart():

    # Retrieve selected registration IDs
    id_list = request.form.getlist('registration_ids')  # ['1', '2', '3']
    print(request.form)
    print(id_list)
    
    # Initialize counters and flags
    added_count = 0
    invalid_payments = []

    # Process each ID
    for registration_id in id_list:
        registration = Registration.query.get(str(registration_id))
       
        
        if registration.event:
            # Validate payment status
            if registration.status.lower() in ['paid', 'pending']:
                invalid_payments.append(registration_id)
                continue  # Skip adding this registration
            
            # Fetch event price through the relationship
            price = registration.event.price  # Assuming relationship exists
            # Create a new Cart entry
            new_cart_item = CartEvent(
                registration_id=str(registration.id),
                price =registration.event.price
            )
            db.session.add(new_cart_item)
            added_count += 1

    # Commit the changes for valid entries
    db.session.commit()
    
    # Flash appropriate messages
    if invalid_payments:
        flash(
            f"Some registrations were not added due to incomplete payment: {', '.join(invalid_payments)}.",
            category="warning"
        )
    
    if added_count > 0:
        flash(f"Successfully added {added_count} registrations to the cart!", category="success")
    else:
        flash("No registrations were added to the cart. Please check payment status.", category="error")
    
    return redirect('/cart')
    
@app.route('/remove_from_cart/<int:cart_id>', methods=['GET'])
def remove_from_cart(cart_id):
    # Find the cart entry by its ID
    cart_entry = CartEvent.query.get(cart_id)

    if cart_entry:
        # Delete the entry from the database
        db.session.delete(cart_entry)
        db.session.commit()
        flash(f"Item with ID {cart_id} removed from the cart.", category="success")
    else:
        flash(f"Item with ID {cart_id} not found.", category="error")

    # Redirect back to the cart page
    return redirect('/cart')


@app.route('/checkout_event', methods=['GET', 'POST'])
def checkout_event():
    # Fetch all cart items
    cart_items = CartEvent.query.all()

    registrations = (
        db.session.query(Registration)
        .join(CartEvent, CartEvent.registration_id == Registration.id)
        .all()
    )

    # Determine the payment status based on payment option
    payment_option = session.get('payment_option', 'Cash on Delivery')  # Default to 'Cash on Delivery'
    payment_status = "Pending" if payment_option == "Cash on Delivery" else "Paid"

    if request.method == 'POST':
        # Customer details
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        contact = request.form.get('contact')
        address = request.form.get('address')
        zip_code = request.form.get('zip_code')
        state = request.form.get('state')

        # Fetch competition names only for registrations in the cart
        competitions_registered = ", ".join(
            [reg.competition_name for reg in registrations]
        )

        # Calculate total amount from cart entries
        total_amount = sum(entry.price for entry in cart_items)

        # Save customer data
        new_customer = Customer(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            email=email,
            contact=contact,
            address=address,
            zip_code=zip_code,
            state=state,
            competitions_registered=competitions_registered,
            total_amount=total_amount
        )
        db.session.add(new_customer)
        db.session.commit()

        # Store customer and payment data in session
        session['shipping_data'] = {
            'first_name': first_name,
            'middle_name': middle_name,
            'last_name': last_name,
            'email': email,
            'contact': contact,
            'address': address,
            'zip_code': zip_code,
            'state': state,
            'competitions_registered': competitions_registered,
            'total_amount': total_amount
        }

        return redirect(url_for('payment_event'))  # Redirect to the payment page

    return render_template(
        'checkout_event.html',
        registrations=registrations,
        cart_items=cart_items
    )



@app.route('/payment_event', methods=['GET', 'POST'])
def payment_event():
    if request.method == 'POST':
        # Get payment option from the form
        payment_option = request.form.get('payment_option')
        session['payment_option'] = payment_option

        # Retrieve customer details from the session
        shipping_data = session.get('shipping_data', {})
        customer_email = shipping_data.get('email')

        # Fetch the customer using their email
        customer = Customer.query.filter_by(email=customer_email).first()
        if not customer:
            flash("Customer not found!", "error")
            return redirect(url_for('checkout_event'))

        # Get all cart items based on registration_id (assuming cart has a registration_id column)
        cart_items = CartEvent.query.all()

        # Create a list to store event details
        event_details = []
        for cart_item in cart_items:
            # Fetch the registration based on registration_id in Cart
            registration = Registration.query.filter_by(id=cart_item.registration_id).first()

            if registration:
                # Fetch the event based on event_id in Registration
                event = Event.query.get(registration.event_id)
                if event:
                    event_details.append({
                        "competition_name": event.name,
                        "event_id": event.id,
                        "registration_id": registration.id,
                        "venue": event.venue,
                        "date": event.date
                    })

        # Determine payment status
        payment_status = 'Pending' if payment_option == 'Cash On Delivery' else 'Paid'

        # Create a payment entry
        payment = Payment(
            customer_id=customer.id,
            amount=shipping_data.get('total_amount', 0),
            payment_method=payment_option,
            payment_status=payment_status
        )
        db.session.add(payment)
        db.session.commit()

        # Update registration status based on payment
        for cart_item in cart_items:
            registration = Registration.query.filter_by(id=cart_item.registration_id).first()
            if registration:
                registration.status = 'Paid' if payment_status == 'Paid' else 'Pending'
                db.session.add(registration)

        db.session.commit()
        

        # Send email notification with event details and payment status
        send_email_notification(
            customer_name=customer.first_name,
            customer_email=customer.email,
            event_details=event_details,
            payment_status=payment_status,
            payment_option=payment_option,
            amount_paid=shipping_data.get('total_amount'),
            amount_to_be_paid=None if payment_status == "Paid" else shipping_data.get('total_amount')
        )

        flash("Payment successful!", "success")
        return redirect(url_for('order_summary'))

    # Retrieve shipping data from session
    shipping_data = session.get('shipping_data', {})
    return render_template('payment_event.html', **shipping_data)

def send_email_notification(customer_name, customer_email, event_details, payment_status, payment_option, amount_paid, amount_to_be_paid=None):
    # Prepare details for each event
    event_details_str = ""
    for event in event_details:
        event_details_str += f"""
        <p><strong>Event Name:</strong> {event['competition_name']}<br>
        <strong>Date:</strong> {event['date'].strftime('%Y-%m-%d')}<br>
        <strong>Venue:</strong> {event['venue']}</p>
        """

    # Determine the payment content
    if payment_status.lower() == "paid":
        payment_details = f"""
        <p><strong>Payment Status:</strong> {payment_status}<br>
        <strong>Payment Option:</strong> {payment_option}<br>
        <strong>Amount Paid:</strong> ₹{amount_paid}</p>
        """
    else:
        payment_details = f"""
        <p><strong>Payment Status:</strong> {payment_status}<br>
        <strong>Payment Option:</strong> {payment_option}<br>
        <strong>Amount to be Paid:</strong> ₹{amount_to_be_paid}</p>
        """

    # Compose the email body (HTML format)
    email_body = f"""
    <html>
    <body>
    <p>Dear {customer_name},</p>

    <p>Thank you for registering for the following events:</p>
    {event_details_str}

    {payment_details}

    <p>We look forward to seeing you at the events at 10 a.m.</p>
    <p>Thank you for choosing Pet Haven!</p>

    <p>Best regards,<br>
    Pet Haven Team</p>
    </body>
    </html>
    """

    # Send the email
    try:
        msg = Message(
            subject="Event Registration Confirmation",
            recipients=[customer_email],
            html=email_body  # Send HTML email
        )
        notif_mail.send(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")





@app.route('/order_summary')
def order_summary():
    registrations = Registration.query.all()
    cart_entries= CartEvent.query.all()
    
    total_price = sum(entry.price for entry in cart_entries)

    # Get customer details from session
    shipping_data = session.get('shipping_data', {})
    payment_option = session.get('payment_option')

    for cart_item in cart_entries:
            db.session.delete(cart_item)

    db.session.commit()
    

    return render_template('order_summary.html', 
                           registrations=registrations, 
                           total_price=total_price, 
                           
                           **shipping_data,
                           payment_option=payment_option,cart_entries=cart_entries)


# TEAM 3 CODE AND API

@app.route('/services')
def services():
    services = Service.query.all()
    return render_template('services.html', services=services)


@app.route('/trainer')
def trainer():
    # if 'user' not in session:
    #     flash('Please login first!', 'danger')
    #     return redirect(url_for('login'))
    services = Service.query.all()
    trainers = Service_Provider.query.all()
    # trainer_img_url = f'static/trainer{{trainers.service_provider_id}}.jpg'
    print(trainers)
    print(services)
    return render_template('trainer.html', services=services,trainers = trainers)

@app.route("/add_to_cart_trainers", methods=['POST'])
def add_cart():
    try:
        data = request.get_json()
        user_id = 1
        service_provider_id = data.get('service_provider_id')
        booking_date = data.get('booking_date')
        booking_time = data.get('booking_time')

        booking_date = datetime.strptime(booking_date, '%Y-%m-%d').date()

        # Convert booking_time string to a time object
        booking_time = datetime.strptime(booking_time, '%H:%M').time()

        print(f"service_provider_id: {service_provider_id}, booking_date: {booking_date}, booking_time: {booking_time}")
        final_cart = Final_Cart(user_id=user_id, service_provider_id=service_provider_id, booking_date=booking_date, booking_time=booking_time)
        db.session.add(final_cart)
        db.session.commit()
        return redirect(url_for('view_cart'))
    except Exception as e:
        print(f"Error in add_cart: {str(e)}")
        return jsonify({'error': 'Error adding to cart'}), 500

@app.route('/static/images/trainer/<int:trainer_id>')
def trainer_image(trainer_id):
    return f"static/images/trainer{trainer_id}.jpg"

@app.route('/booking')
def booking():
    service_id = request.args.get('service_id')
    provider_id = request.args.get('provider_id')
    
    service = Service.query.get(service_id) if service_id else None
    provider = Service_Provider.query.get(provider_id) if provider_id else None

    # cart_item_ids = [item.service_provider_id for item in Cart.query.all()]
    
    return render_template('booking.html', service=service, provider=provider)


@app.route('/api/slots', methods=['GET'])
def get_available_slots():
    try:
        date = request.args.get('date')
        provider_id = request.args.get('provider_id')
        
        if not date or not provider_id:
            return jsonify({'error': 'Date and provider ID are required'}), 400
            
        # Convert string date to datetime object
        booking_date = datetime.strptime(date, '%Y-%m-%d').date()
        
        # Get all bookings for this provider on this date
        existing_bookings = Booking.query.filter_by(
            provider_id=provider_id,
            booking_date=booking_date
        ).all()

        # Generate time slots from 9 AM to 5 PM
        slots = []
        start_time = datetime.strptime('09:00', '%H:%M').time()
        end_time = datetime.strptime('17:00', '%H:%M').time()
        
        current_time = datetime.combine(booking_date, start_time)
        end_datetime = datetime.combine(booking_date, end_time)
        
        # Create one-hour slots
        while current_time <= end_datetime:
            current_slot_time = current_time.time()
            
            # Check if slot is booked
            is_booked = any(
                booking.booking_time == current_slot_time 
                for booking in existing_bookings
            )
            
            slots.append({
                'time': current_slot_time.strftime('%H:%M'),
                'isBooked': is_booked
            })
            
            current_time += timedelta(hours=1)
        
        return jsonify(slots)
        
    except Exception as e:
        print(f"Error in get_available_slots: {str(e)}")
        return jsonify({'error': 'Error fetching slots'}), 500
    
def add_cart():
    try:
        data = request.get_json()
        user_id = 1
        service_provider_id = data.get('service_provider_id')
        booking_date = data.get('booking_date')
        booking_time = data.get('booking_time')

        booking_date = datetime.strptime(booking_date, '%Y-%m-%d').date()

        # Convert booking_time string to a time object
        booking_time = datetime.strptime(booking_time, '%H:%M').time()

        print(f"service_provider_id: {service_provider_id}, booking_date: {booking_date}, booking_time: {booking_time}")
        final_cart = Final_Cart(user_id=user_id, service_provider_id=service_provider_id, booking_date=booking_date, booking_time=booking_time)
        db.session.add(final_cart)
        db.session.commit()
        return redirect(url_for('show_cart'))
    except Exception as e:
        print(f"Error in add_cart: {str(e)}")
        return jsonify({'error': 'Error adding to cart'}), 500
    
@app.route("/delete_to_cart/<int:id>")
def delete_cart(id):
    cart_item = Final_Cart.query.get(id)
    if cart_item:
        # Delete the corresponding booking from CartBooking
        cart_item = Final_Cart.query.filter_by(id = id).first()
        if cart_item:
            db.session.delete(cart_item)
        
        # Delete the corresponding booking from Booking
        # booking = Booking.query.filter_by(provider_id=service_provider_id).first()
        # if booking:
        #     db.session.delete(booking)
        db.session.commit()
        flash("Item removed from cart successfully!", "success")
    return redirect('/cart')

@app.route('/api/book_slot', methods=['POST'])
def book_slot():
    try:
        data = request.json
        provider_id = data['provider_id']
        booking_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        booking_time = datetime.strptime(data['time'], '%H:%M').time()

        # Check if the slot is already booked
        existing_booking = Booking.query.filter_by(
            provider_id=provider_id,
            booking_date=booking_date,
            booking_time=booking_time
        ).first()

        if existing_booking:
            return jsonify({'error': 'This slot is already booked.'}), 400

        # Save the booking
        # booking = Booking(
        #     name='Temporary Name',  # Replace with actual user data
        #     email='Temporary Email',  # Replace with actual user data
        #     phone='Temporary Phone',  # Replace with actual user data
        #     service_id=1,  # Replace with actual service ID
        #     provider_id=provider_id,
        #     booking_date=booking_date,
        #     booking_time=booking_time
        # )
        # db.session.add(booking)
        # db.session.commit()

        # Save booking to CartBooking for temporary storage
        # cart_booking = CartBooking(
        #     cart_id=provider_id,
        #     booking_date=booking_date,
        #     booking_time=booking_time
        # )
        # cart_booking.is_booked = True
        # db.session.add(cart_booking)
        # db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error in book_slot: {str(e)}")
        return jsonify({'error': 'Error booking slot'}), 500
    
# @app.route('/cart', methods=['GET'])
# def show_cart():
#     try:
#         # Get cart items
#         # cart_items = Cart.query.all()
#         # cart_items = Final_Cart.query.all()
#         # trainers = []

#         # for item in cart_items:
#         #     trainer = Service_Provider.query.get(item.service_provider_id)
#         #     if trainer:
#         #         trainers.append(trainer)
#         cart_items = Final_Cart.query.all()
#         cart_info = []
#         for item in cart_items:
#             trainer = Service_Provider.query.get(item.service_provider_id)
#             if trainer:
#                 d = {
#                     'id': item.id,
#                     'name': trainer.name,
#                     'service_provider_id': item.service_provider_id,
#                     'booking_time': item.booking_time,
#                     "booking_date": item.booking_date,
#                     'cost': trainer.cost
#                 }
#                 cart_info.append(d)
#         # Calculate costs
#         print(f"Cart info: {cart_info}")
#         cost = sum(item['cost'] or 0 for item in cart_info)
#         taxes = int(cost * 0.18)
#         total_amount = cost + taxes
#         cart_count = len(cart_info)

#         # Store cart summary in session for later use
#         session['cart_summary'] = {
#             'cost': cost,
#             'taxes': taxes,
#             'total_amount': total_amount,
#             'cart_count': cart_count
#         }
#         print(f"Cart summary: {session['cart_summary']}")

#         return render_template(
#             'cart.html',
#             cart_info = cart_info,
#             cart_cost = cost,
#             taxes = taxes,
#             total_amount = total_amount,


#         )

#     except Exception as e:
#         print(f"Error in show_cart: {str(e)}")
#         return jsonify({'error': str(e)}), 500

@app.route('/initiate_cart_checkout', methods=['GET'])
def initiate_cart_checkout():
    try:
        cart_items = Final_Cart.query.all()
        if not cart_items:
            return jsonify({'message': 'Your cart is empty.'})

        # Store cart items in session
        session['cart_items'] = [item.service_provider_id for item in cart_items]
        print(f'Cart items: {session["cart_items"]}')
        # Redirect to shipping details page
        return jsonify({'redirect_url': url_for('shipping_details')})
    except Exception as e:
        print(f"Error in initiate_cart_checkout: {str(e)}")
        return jsonify({'error': str(e)}), 500


# @app.route('/shipping_details', methods=['GET', 'POST'])
# def shipping_details():
#     if request.method == 'POST':
#         try:
#             # Create new shipping details record
#             shipping = ShippingDetails(
#                 first_name=request.form['first_name'],
#                 middle_name=request.form['middle_name'],
#                 last_name=request.form['last_name'],
#                 email=request.form['email'],
#                 contact=request.form['contact'],
#                 address=request.form['address'],
#                 zip_code=request.form['zip_code'],
#                 state=request.form['state']
#             )
#             db.session.add(shipping)
#             db.session.commit()
            
#             # Store shipping ID in session
#             session['shipping_details'] = {
#                 'first_name': shipping.first_name,
#                 'middle_name': shipping.middle_name,
#                 'last_name': shipping.last_name,
#                 'email': shipping.email,
#                 'contact': shipping.contact,
#                 'address': shipping.address,
#                 'zip_code': shipping.zip_code,
#                 'state': shipping.state
#             }
#             print(f'In the function shippinh details Shipping details: {session["shipping_details"]}')
#             return redirect(url_for('payment'))
            
#         except Exception as e:
#             print(f"Error in shipping_details POST: {str(e)}")
#             db.session.rollback()
#             return redirect(url_for('shipping_details'))

#     return render_template('shipping.html')


# @app.route('/payment', methods=['GET', 'POST'])
# def payment():
#     if request.method == 'POST':
#         try:
#             # Get payment details
#             payment_option = request.form.get('payment_option')
            
#             if not payment_option:
#                 return jsonify({
#                     'success': False,
#                     'error': 'Please select a payment method'
#                 }), 400
            
#             # Store payment method in session
#             session['payment_option'] = payment_option
            
#             # Get shipping details and cart summary from session
#             shipping_details = session.get('shipping_details', {})
#             print(f"In the function payemtn Shipping details: {shipping_details}")
#             cart_summary = session.get('cart_summary', {})
#             print(f"In the function payment Cart summary: {cart_summary}")
            
#             # Store order details in session for success page
#             session['order_details'] = {
#                 'shipping_details': shipping_details,
#                 'cart_summary': cart_summary,
#                 'payment_option': payment_option,
#                 'order_date': datetime.now().strftime('%B %d, %Y'),
#                 'expected_delivery_date': (datetime.now() + timedelta(days=7)).strftime('%B %d, %Y')
#             }
#             print(session['order_details'])
            
#             # return jsonify({
#             #     'success': True,
#             #     'redirect_url': url_for('success')
#             # })
#             cart_items = Final_Cart.query.all()
#             for item in cart_items:
#                 booking = Booking(
#                     name=shipping_details['first_name'] + ' ' + shipping_details['last_name'],
#                     email=shipping_details['email'],
#                     phone=shipping_details['contact'],
#                     service_id=Service.query.get(item.service_provider_id).id,
#                     provider_id=item.service_provider_id,
#                     booking_date=item.booking_date,
#                     booking_time=item.booking_time
#                 )
#                 db.session.add(booking)
#                 db.session.commit()
#             return redirect('/success')
            
#         except Exception as e:
#             print(f"Error in payment POST: {str(e)}")
#             return jsonify({
#                 'success': False,
#                 'error': str(e)
#             }), 500

    # GET request - show payment page
    try:
        shipping_details = session.get('shipping_details', {})
        cart_summary = session.get('cart_summary', {})
        
        return render_template('payment.html',
                             first_name=shipping_details.get('first_name', ''),
                             middle_name=shipping_details.get('middle_name', ''),
                             last_name=shipping_details.get('last_name', ''),
                             email=shipping_details.get('email', ''),
                             contact=shipping_details.get('contact', ''),
                             address=shipping_details.get('address', ''),
                             cart_summary=cart_summary)
    except Exception as e:
        print(f"Error rendering payment page: {str(e)}")
        return redirect(url_for('index'))
    
@app.route('/success')
def success():
    try:
        # ! Add Cart items 2 to sales 
        # ! Add Cart item 3 to Booking 
        # Get order details from session
        order_details = session.get('order_details', {})
        if not order_details:
            print("No order details found in session")
            return redirect(url_for('home'))

        shipping_details = order_details.get('shipping_details', {})
        cart_summary = order_details.get('cart_summary', {})
        payment_option = order_details.get('payment_option')
        # Get cart items for order details
        cart_items = Final_Cart.query.all()
        cart_details = []
        for item in cart_items:
            trainer = Service_Provider.query.get(item.service_provider_id)
            if trainer:
                cart_details.append({
                    'name': trainer.name,
                    'price': trainer.cost,
                    'quantity': 1,
                    'total': trainer.cost
                })
       # Send confirmation email
        try:
            msg = Message(
                'Booking Confirmation - PetCare Services',
                sender=app.config['MAIL_USERNAME'],
                recipients=[shipping_details.get('email')]
            )
            
            # Create email body based on payment option
            if payment_option == 'Cash On Delivery':
                email_body = f"""Hello {shipping_details.get('first_name')},

Thank you for booking with PetCare Services! Your booking has been confirmed.

Booking Details:
- Order Date: {order_details.get('order_date')}
- Expected Service Date: {order_details.get('expected_delivery_date')}

Services Booked:
{chr(10).join([f"- {item['name']}: Rs. {item['price']}" for item in cart_details])}

Payment Information:
- Payment Method: Cash On Delivery
- Amount to be Paid: Rs. {cart_summary.get('total_amount', 0) + 50}

Please keep cash ready during the service delivery.

Thank you for choosing PetCare Services!

Best regards,
PetCare Team"""
            else:
                email_body = f"""Hello {shipping_details.get('first_name')},

Thank you for booking with PetCare Services! Your booking and payment have been confirmed.

Booking Details:
- Order Date: {order_details.get('order_date')}
- Expected Service Date: {order_details.get('expected_delivery_date')}

Services Booked:
{chr(10).join([f"- {item['name']}: Rs. {item['price']}" for item in cart_details])}

Payment Information:
- Payment Method: {payment_option}
- Amount Paid: Rs. {cart_summary.get('total_amount', 0) + 50}

Thank you for choosing PetCare Services!

Best regards,
PetCare Team"""

            msg.body = email_body
            notif_mail.send(msg)
        except Exception as e:
            print(f"Error sending email: {str(e)}")

        # Clear cart after successful order
        for item in cart_items:
            db.session.delete(item)
        db.session.commit()

        # Clear session data
        session.pop('cart_items', None)
        session.pop('shipping_details', None)
        session.pop('cart_summary', None)
        session.pop('payment_option', None)
        session.pop('order_details', None)

        return render_template('success.html',
            current_date=order_details.get('order_date'),
            expected_delivery_date=order_details.get('expected_delivery_date'),
            first_name=shipping_details.get('first_name', ''),
            middle_name=shipping_details.get('middle_name', ''),
            last_name=shipping_details.get('last_name', ''),
            email=shipping_details.get('email', ''),
            contact=shipping_details.get('contact', ''),
            address=shipping_details.get('address', ''),
            payment_option=order_details.get('payment_option'),
            cart_details=cart_details,
            zip_code=shipping_details.get('zip_code', ''),
            state=shipping_details.get('state', ''),
            subtotal=cart_summary.get('cost', 0),
            shipping=50,  # Fixed shipping cost
            tax=cart_summary.get('taxes', 0),
            total=cart_summary.get('total_amount', 0) + 50  # Add shipping cost
        )
    except Exception as e:
        print(f"Error in success page: {str(e)}")
        return redirect(url_for('index'))


@app.route('/success_page')
def success_page():
    shipping_data = session.get('shipping_data', {})
    payment_option = session.get('payment_option')
    current_date = datetime.today().strftime('%Y-%m-%d')
    expected_delivery_date = (datetime.today() + timedelta(days=5)).strftime('%Y-%m-%d')

    sale = Sale(
        buyer_name=f"{shipping_data.get('first_name')} {shipping_data.get('last_name')}",
        sale_price=get_cart_data()['total'],
        payment_method=payment_option,
        invoice_number = str(datetime.now().timestamp()).replace('.', '')
    )

    db.session.add(sale)
    db.session.commit()

    for cart_detail in get_cart_data()['cart_details']:
        sale_detail = Sale_detail(
            sale_id = sale.sale_id,
            breed_name=cart_detail['name'],
            price=cart_detail['price'],
            dog_id=cart_detail['pet_id']
        )
        db.session.add(sale_detail)
        
    for cart_detail in get_cart_data()['cart_details']:
        dog_sales = db.session.query(Dog_sales).filter_by(breed=cart_detail['name']).first()
        if not dog_sales:
         dog_sales = Dog_sales(
            breed=cart_detail['name'],
            quantity=1,
            price=cart_detail['price']
         )
         db.session.add(dog_sales)
        else:
         dog_sales.quantity += 1  # Increment quantity
       # Update pet availability
    for cart_detail in get_cart_data()['cart_details']:
        pet = db.session.query(Pet).filter_by(pet_id=cart_detail['pet_id']).first()
        if pet:
            pet.availability_status = 'sold'

    cart_items = Final_Cart.query.all()
    for item in cart_items:
        booking = Booking(
            name=shipping_data['first_name'] + ' ' + shipping_data['last_name'],
            email=shipping_data['email'],
            phone=shipping_data['contact'],
            service_id=Service_Provider.query.get(item.service_provider_id).service_provided_id,
            provider_id=item.service_provider_id,
            booking_date=item.booking_date,
            booking_time=item.booking_time
        )
        db.session.add(booking)
        db.session.commit()
    # item , price , quantity total
    summary = []
    for cart_detail in get_cart_data()['cart_details']:
        summary.append({
            'item': cart_detail['name'],
            'price': cart_detail['price'],
            'quantity': 1,
            'total': cart_detail['price']
        })
    # item , price , quantity total
    for items in cart_items:
        summary.append({
            'item': Service_Provider.query.get(items.service_provider_id).name,
            'price': Service_Provider.query.get(items.service_provider_id).cost,
            'quantity': 1,
            'total': Service_Provider.query.get(items.service_provider_id).cost
        })

    cart_items = CartEvent.query.all()
    for item in cart_items:
        summary.append({
            'item':Registration.query.get(item.registration_id).competition_name,
            'price': item.price,
            "quantity": 1,
            "total": item.price,
        })


    subtotal = 0 
    for item in summary:
        subtotal += item['price']
    
    shipping = 100
    gst = subtotal * 0.18
    sgst = gst / 2
    total = subtotal + shipping + gst

    db.session.query(Final_Cart).delete()
    db.session.query(Cart).delete()
    db.session.query(CartEvent).delete()
    db.session.commit()

    return render_template(
        'success.html', 
        first_name = shipping_data['first_name'],
        email = shipping_data['email'],
        contact = shipping_data['contact'],
        address = shipping_data['address'],
        zip_code = shipping_data['zip_code'],
        state = shipping_data['state'],
        payment_option=payment_option, current_date=current_date, expected_delivery_date=expected_delivery_date,
        summary=summary,
        subtotal=subtotal,
        shipping=shipping,
        gst=gst,
        sgst=sgst,
        total=total
    )




def setup_image_handling(app):
    # Configure image upload settings
    UPLOAD_FOLDER = os.path.join('static', 'images')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Create upload folders if they don't exist
    os.makedirs(os.path.join(UPLOAD_FOLDER, 'trainers'), exist_ok=True)
    os.makedirs(os.path.join(UPLOAD_FOLDER, 'services'), exist_ok=True)
    
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    @app.route('/upload_trainer_image/<int:trainer_id>', methods=['POST'])
    def upload_trainer_image(trainer_id):
        try:
            if 'image' not in request.files:
                return jsonify({'error': 'No image file provided'}), 400
                
            file = request.files['image']
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400
                
            if file and allowed_file(file.filename):
                # Create a standardized filename for the trainer image
                filename = f'trainer{trainer_id}.jpg'
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'trainers', filename)
                
                # Open and optimize the image
                img = Image.open(file)
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                # Resize to a standard size (e.g., 800x800 max)
                img.thumbnail((800, 800))
                # Save with optimization
                img.save(filepath, 'JPEG', quality=85, optimize=True)
                
                return jsonify({'success': True, 'filename': filename}), 200
            
            return jsonify({'error': 'Invalid file type'}), 400
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/upload_service_image/<int:service_id>', methods=['POST'])
    def upload_service_image(service_id):
        try:
            if 'image' not in request.files:
                return jsonify({'error': 'No image file provided'}), 400
                
            file = request.files['image']
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400
                
            if file and allowed_file(file.filename):
                # Create a standardized filename for the service image
                filename = f'service{service_id}.jpg'
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'services', filename)
                
                # Open and optimize the image
                img = Image.open(file)
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                # Resize to a standard size (e.g., 1200x800 max for service images)
                img.thumbnail((1200, 800))
                # Save with optimization
                img.save(filepath, 'JPEG', quality=85, optimize=True)
                
                return jsonify({'success': True, 'filename': filename}), 200
            
            return jsonify({'error': 'Invalid file type'}), 400
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return {
        'allowed_file': allowed_file,
        'UPLOAD_FOLDER': UPLOAD_FOLDER,
        'ALLOWED_EXTENSIONS': ALLOWED_EXTENSIONS,
        'upload_trainer_image': upload_trainer_image,
        'upload_service_image': upload_service_image
    }

image_handler = setup_image_handling(app)
app.config['UPLOAD_FOLDER'] = image_handler['UPLOAD_FOLDER']

    
@app.route('/admin_services')
def admin_services():
    services = Service.query.all()
    return render_template('admin_services.html', services=services)


@app.route('/admin_trainer')
def admin_trainer():
    services = Service.query.all()
    trainers = Service_Provider.query.all()
    edit_requests = EditRequest.query.order_by(EditRequest.created_at.desc()).all()
    pending_count = EditRequest.query.filter_by(status='pending').count()
    service_list = [{'id': s.id, 'name': s.title} for s in services]
    
    return render_template('admin_trainer.html', 
                         services=services,
                         trainers=trainers,
                         service_list=service_list,
                         edit_requests=edit_requests,
                         pending_count=pending_count)

@app.route('/edit_request/<int:request_id>/update_status', methods=['POST'])
def update_request_status(request_id):
    edit_request = EditRequest.query.get_or_404(request_id)
    status = request.form.get('status')
    if status in ['approved', 'rejected']:
        edit_request.status = status
        db.session.commit()
        flash(f'Request has been {status}', 'success')
    return redirect(url_for('admin_trainer'))

@app.route('/edit_request/<int:request_id>/delete', methods=['POST'])
def delete_request(request_id):
    edit_request = EditRequest.query.get_or_404(request_id)
    
    # Delete associated files
    if edit_request.certifications:
        for file_path in edit_request.certifications.split(','):
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                flash(f'Error deleting file: {str(e)}', 'warning')
    
    db.session.delete(edit_request)
    db.session.commit()
    flash('Request has been deleted', 'success')
    return redirect(url_for('admin_trainer'))
@app.route('/static/images/admin_trainer/<int:trainer_id>')
def admin_trainer_image(trainer_id):
    return f"static/images/trainer/{trainer_id}.jpg"
@app.route('/add_service', methods=['POST'])
def add_service():
    try:
        # Get form data
        title = request.form['title']
        description = request.form['description']
        alt = request.form['alt']
        section_id = request.form['section_id']
        
        # Check if section_id already exists
        existing_service = Service.query.filter_by(section_id=section_id).first()
        if existing_service:
            return jsonify({'error': 'Section ID already exists'}), 400
        
        # Create a new service without the image path first to get the service_id
        new_service = Service(
            image='',  # Temporary placeholder
            alt=alt,
            title=title,
            description=description,
            section_id=section_id
        )
        
        db.session.add(new_service)
        db.session.commit()
        
        # Get the generated service_id
        service_id = new_service.id

        # Handle image upload
        if 'image' in request.files:
            image = request.files['image']
            if image and image.filename:
                extension = image.filename.rsplit('.', 1)[1]
                filename = f"service{service_id}.{extension}"
                original_path = os.path.join(app.config['UPLOAD_FOLDER'], "services", filename)
                image.save(original_path)
                
                # Convert to jpg if necessary
                if extension.lower() != 'jpg':
                    img = Image.open(original_path)
                    img = img.convert('RGB')
                    jpg_filename = f"service{service_id}.jpg"
                    jpg_path = os.path.join(app.config['UPLOAD_FOLDER'], "services", jpg_filename)
                    img.save(jpg_path)
                    os.remove(original_path)
                    new_service.image = f"services/{jpg_filename}"
                else:
                    new_service.image = f"services/{filename}"
        
        db.session.commit()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        print(f"Error adding service: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
@app.route('/edit_service/<int:service_id>', methods=['POST'])
def edit_service(service_id):
    try:
        service = Service.query.get_or_404(service_id)
        
        # Update service fields
        service.title = request.form['title']
        service.description = request.form['description']
        # service.alt = request.form['alt']
        
        # Handle image update if new image is provided
        if 'image' in request.files:
            image = request.files['image']
            if image and image.filename:
                print(f"image = {image}")
                extension = image.filename.rsplit('.', 1)[1]
                filename = f"service{service_id}.{extension}"
                my_file_name = filename.split(".")[0]
                original_path = os.path.join(app.config['UPLOAD_FOLDER'],"services", filename)
                # image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image.save(original_path)
                # if the image is not a jpg, convert it to jpg
                if extension.lower() != 'jpg':
                    img = Image.open(original_path)
                    img = img.convert('RGB')
                    # new_file_name = f"service{service_id}.jpg"
                    # new_path = os.path.join(app.config['UPLOAD_FOLDER'],"services", new_file_name)
                    # img.save(new_path, 'JPG', quality=85, optimize=True)
                    # service.image = f'images/{filename}'
                    jpg_filename = my_file_name + ".jpg"
                    jpg_path = os.path.join(app.config['UPLOAD_FOLDER'],"services",jpg_filename)
                    img.save(jpg_path)
                    os.remove(original_path)
        
        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        print(f"Error updating service: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/delete_service/<int:service_id>', methods=['DELETE'])
def delete_service(service_id):
    try:
        service = Service.query.get_or_404(service_id)
        db.session.delete(service)
        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        print(f"Error deleting service: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    

@app.route('/add_trainer', methods=['POST'])
def add_trainer():
    try:
        # Debugging: Log received form data
        print("Form Data:", request.form)
        print("File Data:", request.files)

        name = request.form['name']
        experience = request.form['experience']
        availability = bool(int(request.form['availability']))
        service_provided_id = request.form['service_provided_id']
        description = request.form.get('description', '')
        location = request.form.get('location', '')
        cost = request.form.get('cost', '')

        new_trainer = Service_Provider(
            name=name,
            experience=experience,
            availability=availability,
            service_provided_id=service_provided_id,
            description=description,
            location=location,
            cost=cost
        )
        db.session.add(new_trainer)
        db.session.commit()
        
        # Handle the image upload using the function from image_handler
        if 'image' in request.files:
            file = request.files['image']
            if file and image_handler['allowed_file'](file.filename):
                # Call upload_trainer_image through the image handler
                return image_handler['upload_trainer_image'](new_trainer.service_provider_id)
        
        return redirect('/admin_trainer')
    except Exception as e:
        print(f"Error adding trainer: {e}")
        db.session.rollback()
        return str(e), 500
    
@app.route('/delete_trainer/<int:service_provider_id>', methods=['DELETE'])
def delete_trainer(service_provider_id):
    try:
        trainer = Service_Provider.query.get_or_404(service_provider_id)
        db.session.delete(trainer)
        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        print(f"Error deleting trainer: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/edit_trainer/<int:service_provider_id>', methods=['POST'])
def edit_trainer(service_provider_id):
    print(f"service provided {service_provider_id}")
    service_provider_id = request.form['service_provider_id']
    name = request.form['name']
    experience = request.form['experience']
    availability = request.form.get('availability', '1')
    description = request.form['description']
    location = request.form['location']
    cost = request.form['cost']
    service_provided_id = request.form['service_provided_id']
    

    # Find the trainer in the database
    trainer = Service_Provider.query.get(service_provider_id)
    if not trainer:
        flash('Trainer not found', 'error')
        return redirect(url_for('admin_trainer'))
    if trainer:
        trainer.name = name
        trainer.experience = experience
        trainer.availability = bool(int(availability))
        trainer.description = description
        trainer.location = location
        trainer.cost = cost
        trainer.service_provided_id = service_provided_id

            # Handle image upload
        if 'image' in request.files:
            image = request.files['image']
            if image and image.filename:
                print(f"image = {image}")
                extension = image.filename.rsplit('.', 1)[1]
                filename = f"trainer{service_provider_id}.{extension}"
                my_file_name = filename.split(".")[0]
                original_path = os.path.join(app.config['UPLOAD_FOLDER'],"trainers", filename)
                # image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image.save(original_path)
                # if the image is not a jpg, convert it to jpg
                if extension.lower() != 'jpg':
                    img = Image.open(original_path)
                    img = img.convert('RGB')
                    # new_file_name = f"service{service_id}.jpg"
                    # new_path = os.path.join(app.config['UPLOAD_FOLDER'],"services", new_file_name)
                    # img.save(new_path, 'JPG', quality=85, optimize=True)
                    # service.image = f'images/{filename}'
                    jpg_filename = my_file_name + ".jpg"
                    jpg_path = os.path.join(app.config['UPLOAD_FOLDER'],"trainers",jpg_filename)
                    img.save(jpg_path)
                    os.remove(original_path)

        db.session.commit()
    flash('Trainer updated successfully', 'success')
    return redirect(url_for('admin_trainer'))

 
@app.route('/static/images/trainer/<path:filename>')
def trainer_images(filename):
    return send_from_directory('static/images/trainer', filename)


app.config['UPLOAD_FOLDER'] = 'static/certificates'
app.config['MAX_CONTENT_LENGTH'] = 20* 1024 * 1024  # 5MB max-limit
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/edit_request', methods=['GET', 'POST'])
def edit_request():
    if request.method == 'POST':
        try:
            # Create upload directory if it doesn't exist
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            # Handle file uploads
            uploaded_files = request.files.getlist('certifications')
            file_paths = []
            
            for file in uploaded_files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Add timestamp to filename to make it unique
                    filename = f"{int(time.time())}_{filename}"
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    file_paths.append(file_path)
                else:
                    flash('Invalid file type. Please upload PDF files only.', 'danger')
                    return redirect(url_for('edit_request'))

            # Get form data
            hashed_password = generate_password_hash(request.form['password']) if request.form['password'] else None
            
            edit_request = EditRequest(
                full_name=request.form['full_name'],
                email=request.form['email'],
                password=hashed_password,
                service_type=request.form['service_type'],
                location=request.form['location'],
                hourly_rate=float(request.form['hourly_rate']),
                certifications=','.join(file_paths),  # Store file paths as comma-separated string
                experience=request.form['experience']
            )
            
            db.session.add(edit_request)
            db.session.commit()
            
            flash('Your edit request has been submitted successfully!', 'success')
            return redirect(url_for('edit_request'))
            
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('edit_request'))
            
    return render_template('edit_request.html')
   
@app.route('/trainer_services')
def trainer_services():
    services = Service.query.all()
    return render_template('trainer_services.html', services=services)

@app.route('/trainer_trainerpg')
def trainer_trainerpg():
    services = Service.query.all()
    trainers = Service_Provider.query.all()
    service_list = [{'id': s.id, 'name': s.title} for s in services]
    # trainer_img_url = f'static/trainer{{trainers.service_provider_id}}.jpg'
    return render_template('trainer_trainerpg.html', services=services,trainers = trainers,service_list=service_list)

@app.route('/trainer_book')
def trainer_book():
    service_id = request.args.get('service_id')
    provider_id = request.args.get('provider_id')
    
    service = Service.query.get(service_id) if service_id else None
    provider = Service_Provider.query.get(provider_id) if provider_id else None

    # cart_item_ids = [item.service_provider_id for item in Cart.query.all()]
    
    return render_template('trainer_book.html', service=service, provider=provider)

#

def fetch_revenue_data(group_by):
    """Fetch revenue data for all sources (Dog Sales, Competitions, Spa Services) aggregated by the specified period."""
    if group_by == 'quarterly':
        period_format = """
            CASE
                WHEN CAST(strftime('%m', sale_date) AS INTEGER) BETWEEN 1 AND 3 THEN strftime('%Y', sale_date) || '-Q1'
                WHEN CAST(strftime('%m', sale_date) AS INTEGER) BETWEEN 4 AND 6 THEN strftime('%Y', sale_date) || '-Q2'
                WHEN CAST(strftime('%m', sale_date) AS INTEGER) BETWEEN 7 AND 9 THEN strftime('%Y', sale_date) || '-Q3'
                WHEN CAST(strftime('%m', sale_date) AS INTEGER) BETWEEN 10 AND 12 THEN strftime('%Y', sale_date) || '-Q4'
            END
        """
    else:
        period_format = {
            'yearly': "strftime('%Y', sale_date)",
            'monthly': "strftime('%Y-%m', sale_date)"
        }[group_by]

    sales_query = text(f"""
        SELECT SUM(sale_price) AS total_sales_revenue, {period_format} AS period
        FROM sales GROUP BY period ORDER BY period DESC
    """)
    competition_query = text(f"""
        SELECT SUM(amount) AS total_competition_revenue, {period_format.replace('sale_date', 'payment_date')} AS period
        FROM payment GROUP BY period ORDER BY period DESC
    """)
    spa_query = text(f"""
        SELECT SUM(total_amount) AS total_spa_revenue, {period_format.replace('sale_date', 'order_date')} AS period
        FROM orders GROUP BY period ORDER BY period DESC
    """)

    sales_data = db.session.execute(sales_query).fetchall()
    competition_data = db.session.execute(competition_query).fetchall()
    spa_data = db.session.execute(spa_query).fetchall()

    sales_df = pd.DataFrame(sales_data, columns=['total_sales_revenue', 'period'])
    competition_df = pd.DataFrame(competition_data, columns=['total_competition_revenue', 'period'])
    spa_df = pd.DataFrame(spa_data, columns=['total_spa_revenue', 'period'])

    merged_df = pd.merge(sales_df, competition_df, on='period', how='outer')
    merged_df = pd.merge(merged_df, spa_df, on='period', how='outer')

    merged_df['total_sales_revenue'] = pd.to_numeric(merged_df['total_sales_revenue'], errors='coerce').fillna(0)
    merged_df['total_competition_revenue'] = pd.to_numeric(merged_df['total_competition_revenue'], errors='coerce').fillna(0)
    merged_df['total_spa_revenue'] = pd.to_numeric(merged_df['total_spa_revenue'], errors='coerce').fillna(0)

    return merged_df

def fetch_individual_revenue(timeframe):
    """Fetch total revenue data for each individual source based on the selected timeframe."""
    period_format = {
        'yearly': "strftime('%Y', sale_date)",
        'monthly': "strftime('%Y-%m', sale_date)",
        'quarterly': """
            CASE
                WHEN CAST(strftime('%m', sale_date) AS INTEGER) BETWEEN 1 AND 3 THEN strftime('%Y', sale_date) || '-Q1'
                WHEN CAST(strftime('%m', sale_date) AS INTEGER) BETWEEN 4 AND 6 THEN strftime('%Y', sale_date) || '-Q2'
                WHEN CAST(strftime('%m', sale_date) AS INTEGER) BETWEEN 7 AND 9 THEN strftime('%Y', sale_date) || '-Q3'
                WHEN CAST(strftime('%m', sale_date) AS INTEGER) BETWEEN 10 AND 12 THEN strftime('%Y', sale_date) || '-Q4'
            END
        """
    }[timeframe]

    sales_query = text(f""" SELECT SUM(sale_price) FROM sales 
        WHERE {period_format} = (SELECT {period_format} FROM sales ORDER BY sale_date DESC LIMIT 1)""")
    
    competition_query = text(f"""   SELECT SUM(amount) FROM payment 
        WHERE {period_format.replace('sale_date', 'payment_date')} =
          (SELECT {period_format.replace('sale_date', 'payment_date')} FROM payment ORDER BY payment_date DESC LIMIT 1)""")
    
    spa_query = text(f"""
        SELECT SUM(total_amount) FROM orders WHERE {period_format.replace('sale_date', 'order_date')} = 
        (SELECT {period_format.replace('sale_date', 'order_date')} FROM orders ORDER BY order_date DESC LIMIT 1)""")

    sales_total = db.session.execute(sales_query).scalar() or 0
    competition_total = db.session.execute(competition_query).scalar() or 0
    spa_total = db.session.execute(spa_query).scalar() or 0

    return {'sales_total': sales_total, 'competition_total': competition_total, 'spa_total': spa_total}

def calculate_growth_rate(df):
    """Calculate the growth rate over time."""
    df['period'] = pd.to_datetime(df['period'], errors='coerce')
    df.dropna(subset=['period'], inplace=True)
    df.sort_values('period', inplace=True)

    # Calculate the total revenue over time
    df['total_revenue'] = df['total_sales_revenue'] + df['total_competition_revenue'] + df['total_spa_revenue']

    # Calculate percentage change in total revenue (growth rate)
    df['growth_rate'] = df['total_revenue'].pct_change() * 100

    return df


def fetch_dog_sales_over_time(group_by):
    """Fetch sales data grouped by time periods for all breeds."""
    if group_by == 'quarterly':
        period_format = """
            CASE
                WHEN CAST(strftime('%m', sale_date) AS INTEGER) BETWEEN 1 AND 3 THEN strftime('%Y', sale_date) || '-Q1'
                WHEN CAST(strftime('%m', sale_date) AS INTEGER) BETWEEN 4 AND 6 THEN strftime('%Y', sale_date) || '-Q2'
                WHEN CAST(strftime('%m', sale_date) AS INTEGER) BETWEEN 7 AND 9 THEN strftime('%Y', sale_date) || '-Q3'
                WHEN CAST(strftime('%m', sale_date) AS INTEGER) BETWEEN 10 AND 12 THEN strftime('%Y', sale_date) || '-Q4'
            END
        """
    else:
        period_format = {
            'yearly': "strftime('%Y', sale_date)",
            'monthly': "strftime('%Y-%m', sale_date)"
        }[group_by]

    query = text(f"""
        SELECT {period_format} AS period, Dog_sales.breed, SUM(Dog_sales.quantity * Dog_sales.price) AS total_revenue
        FROM Dog_sales
        JOIN sale_detail ON Dog_sales.breed_id = sale_detail.dog_id
        JOIN Sales ON sale_detail.sale_id = Sales.sale_id
        GROUP BY period, Dog_sales.breed
        ORDER BY period DESC, total_revenue DESC
    """)
    result = db.session.execute(query).fetchall()
    return pd.DataFrame(result, columns=['period', 'breed', 'total_revenue'])

def fetch_trainer_revenue(group_by):
    """Fetch revenue for each trainer grouped by week, month, or year."""
    if group_by == 'quarterly':
        period_format = """
        CASE
            WHEN CAST(strftime('%m', booking_date) AS INTEGER) BETWEEN 1 AND 3 THEN strftime('%Y', booking_date) || '-Q1'
            WHEN CAST(strftime('%m', booking_date) AS INTEGER) BETWEEN 4 AND 6 THEN strftime('%Y', booking_date) || '-Q2'
            WHEN CAST(strftime('%m', booking_date) AS INTEGER) BETWEEN 7 AND 9 THEN strftime('%Y', booking_date) || '-Q3'
            WHEN CAST(strftime('%m', booking_date) AS INTEGER) BETWEEN 10 AND 12 THEN strftime('%Y', booking_date) || '-Q4'
        END
        """
    else:
        period_format = {
            'yearly': "strftime('%Y', booking_date)",
            'monthly': "strftime('%Y-%m', booking_date)"
        }[group_by]


    query = text(f"""
        SELECT {period_format} AS period, service_provider.name, SUM(cost) AS total_revenue
        FROM service_provider
        JOIN booking ON service_provider.service_provider_id = booking.provider_id
        GROUP BY period, service_provider.name
        ORDER BY period DESC, total_revenue DESC
    """)

    result = db.session.execute(query).fetchall()
    return pd.DataFrame(result, columns=['period', 'trainer_name', 'total_revenue'])


@app.route('/admin_ana', methods=['GET'])
def admin_ana():
    timeframe_chart1 = request.args.get('timeframe_chart1', 'monthly')
    timeframe_chart2 = request.args.get('timeframe_chart2', 'monthly')
    timeframe_chart3 = request.args.get('timeframe_chart3', 'monthly')
    timeframe_chart4 = request.args.get('timeframe_chart4', 'monthly')
    timeframe_chart5 = request.args.get('timeframe_chart5', 'monthly')  # Default timeframe is 'monthly'

    merged_df_chart1 = fetch_revenue_data(timeframe_chart1)
    revenue_data_chart2 = fetch_individual_revenue(timeframe_chart2)
    growth_df_chart3 = calculate_growth_rate(fetch_revenue_data(timeframe_chart3))
    sales_over_time_df_chart4= fetch_dog_sales_over_time(timeframe_chart4)
    trainer_revenue_df_chart5 = fetch_trainer_revenue(timeframe_chart5)

    
    # Total Revenue by Source 
    total_revenue_fig_chart1 = px.bar(
        merged_df_chart1,
        x='period',
        y=['total_sales_revenue', 'total_competition_revenue', 'total_spa_revenue'],
        title=f'Revenue Trends by Source over Time ({timeframe_chart1.capitalize()})',
        labels={'period': 'Time Period', 'value': 'Revenue', 'variable': 'Revenue Source'},
        barmode='group'
    )
    total_revenue_graph_html_chart1 = pio.to_html(total_revenue_fig_chart1, full_html=False)

    # Revenue Distribution by Source 
    revenue_df_chart2 = pd.DataFrame({
        'source': ['Sales', 'Competitions', 'Spa'],
        'total_revenue': [
            revenue_data_chart2['sales_total'],
            revenue_data_chart2['competition_total'],
            revenue_data_chart2['spa_total']
        ]
    })
    pie_chart_fig_chart2 = px.pie(
        revenue_df_chart2,
        names='source',
        values='total_revenue',
        title=f'Revenue Distribution by Source ({timeframe_chart2.capitalize()})'
    )
    pie_chart_graph_html_chart2 = pio.to_html(pie_chart_fig_chart2, full_html=False)

    # Revenue Growth Rate Over Time 
    growth_rate_fig_chart3 = px.line(
        growth_df_chart3,
        x='period',
        y='growth_rate',
        title=f'Overall Revenue Growth Rate ({timeframe_chart3.capitalize()})',
        labels={'period': 'Time Period', 'growth_rate': 'Growth Rate (%)'},
        markers=True
    )
    growth_rate_graph_html_chart3 = pio.to_html(growth_rate_fig_chart3, full_html=False)

    # Dog Sales Comparison by Revenue 
    sales_over_time_fig = px.bar(
        sales_over_time_df_chart4,
        x='period',
        y='total_revenue',
        color='breed',
        title=f'Dog Sales Trend Analysis ({timeframe_chart4.capitalize()})',
        labels={'period': 'Time Period', 'total_revenue': 'Total Revenue', 'breed': 'Breed'},
         barmode='group'
      
    )
    sales_over_time_graph_html = pio.to_html(sales_over_time_fig, full_html=False)
    # Trainer Revenue by Time
    trainer_revenue_fig_chart5 = px.bar(
        trainer_revenue_df_chart5,
        x='period',
        y='total_revenue',
        color='trainer_name',
        title=f'Trainer Performance Trends ({timeframe_chart5.capitalize()})',
        labels={'period': 'Time Period', 'total_revenue': 'Total Revenue', 'trainer_name': 'Trainer'},
        barmode='group'
    )
    trainer_revenue_graph_html_chart5 = pio.to_html(trainer_revenue_fig_chart5, full_html=False)

    return render_template(
        'admin_ana.html',
        total_revenue_graph_html=total_revenue_graph_html_chart1,
        pie_chart_graph_html=pie_chart_graph_html_chart2,
        growth_rate_graph_html=growth_rate_graph_html_chart3,
        sales_over_time_graph_html=sales_over_time_graph_html,
        trainer_revenue_graph_html=trainer_revenue_graph_html_chart5,
        timeframe_chart1=timeframe_chart1,
        timeframe_chart2=timeframe_chart2,
        timeframe_chart3=timeframe_chart3,
        timeframe_chart4=timeframe_chart4,
        timeframe_chart5=timeframe_chart5
    )


if __name__ == '__main__':
    # with app.app_context():
    #     db.create_all()
    # with the app funationalities inlclude all the features 
    app.run(debug=True)
