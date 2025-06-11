import os
import unittest
from io import BytesIO
from unittest.mock import patch
from app import app, db, User, otp_store

class TestApp(unittest.TestCase):

    def setUp(self):
        """Set up the test client and the database before each test."""
        self.app = app.test_client()
        self.app.testing = True
        
        with app.app_context():
            db.create_all()  # Create all tables before each test

    def tearDown(self):
        """Clean up after each test."""
        with app.app_context():
            db.session.remove()
            db.drop_all()  # Drop all tables after each test

    def test_register_user(self):
        """Test user registration with valid data."""
        user_data = {
            'fullname': 'John Doe',
            'email': 'johndoe@example.com',
            'password': 'testpassword',
            'confirm_password': 'testpassword',
            'role': 'service-provider',
            'service_type': 'grooming',
            'location': 'New Delhi',
            'hourly_rate': '50',
            'certifications': 'Certified groomer',
            'experience': '5'
        }
        response = self.app.post('/register', json=user_data)
        response_json = response.get_json()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['message'], 'Registration successful')
        self.assertEqual(response_json['role'], 'service-provider')
        self.assertEqual(response_json['fullname'], 'John Doe')

    def test_register_user_missing_fields(self):
        """Test registration with missing required fields."""
        user_data = {
            'fullname': '',  # Missing full name
            'email': 'johndoe@example.com',  
            'password': 'testpassword',
            'confirm_password': 'testpassword',
            'role': 'service-provider',
            'service_type': 'grooming',
            'location': 'New Delhi',
            'hourly_rate': '50',
            'certifications': '',
            'experience': '5'
        }
        response = self.app.post('/register', json=user_data)
        response_json = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response_json)
        self.assertIn('fullname is required', response_json['error'])

    def test_register_user_invalid_email(self):
        """Test registration with an invalid email."""

        # Case 1: Invalid email format (missing @)
        user_data_invalid_at = {
            'fullname': 'John Doe',
            'email': 'invalidemail.com',  # Missing '@'
            'password': 'testpassword',
            'confirm_password': 'testpassword',
            'role': 'service-provider',
            'service_type': 'grooming',
            'location': 'New Delhi',
            'hourly_rate': '50',
            'certifications': 'Certified groomer',
            'experience': '5'
        }
        response_invalid_at = self.app.post('/register', json=user_data_invalid_at)
        response_json_invalid_at = response_invalid_at.get_json()

        self.assertEqual(response_invalid_at.status_code, 400)
        self.assertIn('Invalid email address. Please use a valid format like name@example.com.', response_json_invalid_at['error'])


    def test_register_user_missing_dotcom(self):
        """Test registration with missing .com in the email."""

        # Case 2: Missing '.com' in email
        user_data_missing_dotcom = {
            'fullname': 'John Doe',
            'email': 'invalidemail@domain',  # Missing '.com'
            'password': 'testpassword',
            'confirm_password': 'testpassword',
            'role': 'service-provider',
            'service_type': 'grooming',
            'location': 'New Delhi',
            'hourly_rate': '50',
            'certifications': 'Certified groomer',
            'experience': '5'
        }
        response_missing_dotcom = self.app.post('/register', json=user_data_missing_dotcom)
        response_json_missing_dotcom = response_missing_dotcom.get_json()

        self.assertEqual(response_missing_dotcom.status_code, 400)
        self.assertIn('Invalid email address. Please use a valid format like name@example.com.', response_json_missing_dotcom['error'])


    def test_register_user_invalid_email_format(self):
        """Test registration with a completely invalid email format."""

        # Case 3: Completely invalid email format
        user_data_invalid_format = {
            'fullname': 'John Doe',
            'email': 'invalid-email',  # Invalid email format
            'password': 'testpassword',
            'confirm_password': 'testpassword',
            'role': 'service-provider',
            'service_type': 'grooming',
            'location': 'New Delhi',
            'hourly_rate': '50',
            'certifications': 'Certified groomer',
            'experience': '5'
        }
        response_invalid_format = self.app.post('/register', json=user_data_invalid_format)
        response_json_invalid_format = response_invalid_format.get_json()

        self.assertEqual(response_invalid_format.status_code, 400)
        self.assertIn('Invalid email address. Please use a valid format like name@example.com.', response_json_invalid_format['error'])


    def test_register_user_password_mismatch(self):
        """Test registration with mismatched passwords."""
        user_data = {
            'fullname': 'John Doe',
            'email': 'johndoe@example.com',
            'password': 'testpassword',
            'confirm_password': 'differentpassword',  # Passwords do not match
            'role': 'service-provider',
            'service_type': 'grooming',
            'location': 'New Delhi',
            'hourly_rate': '50',
            'certifications': 'Certified groomer',
            'experience': '5'
        }
        response = self.app.post('/register', json=user_data)
        response_json = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertIn('Passwords do not match', response_json['error'])

    def test_register_user_missing_hourly_rate(self):
        """Test registration with a missing hourly rate."""
        user_data = {
            'fullname': 'John Doe',
            'email': 'johndoe@example.com',
            'password': 'testpassword',
            'confirm_password': 'testpassword',
            'role': 'service-provider',
            'service_type': 'grooming',
            'location': 'New Delhi',
            'hourly_rate': '',  # Missing hourly rate
            'certifications': 'Certified groomer',
            'experience': '5'
        }
        response = self.app.post('/register', json=user_data)
        response_json = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertIn('hourly_rate is required for service providers', response_json['error'])

    def test_register_user_missing_experience(self):
        """Test registration with a missing experience."""
        user_data = {
            'fullname': 'John Doe',
            'email': 'johndoe@example.com',
            'password': 'testpassword',
            'confirm_password': 'testpassword',
            'role': 'service-provider',
            'service_type': 'gromming',
            'location': 'New Delhi',
            'hourly_rate': '50',
            'certifications': 'Certified groomer',
            'experience': ''  # Missing experience
        }
        response = self.app.post('/register', json=user_data)
        response_json = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertIn('experience is required for service providers', response_json['error'])

    @patch('app.otp_store', {'johndoe@example.com': '123456'})
    def test_verify_otp_email_sent(self):
        """Test that a confirmation email is sent upon successful OTP verification and registration."""
        # Mock session
        with self.app.session_transaction() as session:
            session['temp_email'] = 'johndoe@example.com'

        # Mock user data
        user_data = {
            'otp': '123456',
            'password': 'testpassword',
            'fullname': 'John Doe',
            'role': 'service-provider',
            'service_type': 'grooming',
            'location': 'New Delhi',
            'hourly_rate': '50',
            'certifications': 'Certified groomer',
            'experience': '5'
        }

        with patch('app.mail.send') as mock_mail_send:  # Mock mail sending
            response = self.app.post('/verify-otp', json=user_data)
            response_json = response.get_json()

            # Verify the response
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response_json['status'], 'success')
            self.assertIn('Registration successful!', response_json['message'])

            # Verify the email sending functionality
            mock_mail_send.assert_called_once()
            sent_message = mock_mail_send.call_args[0][0]  # Get the first argument of the mail.send() call

            # Check the email content
            self.assertEqual(sent_message.subject, 'Registration Successful - PetCare')
            self.assertEqual(sent_message.sender, 'jasnavig9@gmail.com')  # Replace with your actual sender email
            self.assertIn('Hello John Doe,', sent_message.body)
            self.assertIn('Your registration with PetCare was successful.', sent_message.body)
            self.assertIn('Welcome to our platform!', sent_message.body)



    def test_send_otp(self):
            """Test sending OTP for registration."""
            response = self.app.post('/send-otp', json={'email': 'johndoe@example.com'})
            response_json = response.get_json()

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response_json['status'], 'success')
            self.assertIn('OTP sent to your email', response_json['message'])

    def test_upload_documents(self):
        """Test document upload with different emails in each case."""
        
        # Test Case 1: Upload with one email
        user_data_1 = {
            'fullname': 'John Doe',
            'email': 'johndoe1@example.com',
            'password': 'testpassword',
            'confirm_password': 'testpassword',
            'role': 'service-provider',
            'service_type': 'plumbing',
            'location': 'New Delhi',
            'hourly_rate': '50',
            'certifications': 'Certified groomer',
            'experience': '5'
        }
        self.app.post('/register', json=user_data_1)
        
        # Simulate login for the first user
        login_response_1 = self.app.post('/login', json={'email': 'johndoe1@example.com', 'password': 'testpassword', 'role': 'service-provider'})
        login_response_json_1 = login_response_1.get_json()
        self.assertEqual(login_response_1.status_code, 200)
        self.assertEqual(login_response_json_1['status'], 'success')

        # Set the session email manually for the first user
        with self.app.session_transaction() as session:
            session['temp_email'] = 'johndoe1@example.com'

        # Upload documents for the first user
        files_1 = {
            'id-proof': (BytesIO(b'fake id proof content'), 'id-proof.pdf'),
            'qualification': (BytesIO(b'fake qualification content'), 'qualification.pdf')
            
        }
        
        response_1 = self.app.post('/upload', data=files_1, follow_redirects=True)
        self.assertEqual(response_1.status_code, 200)
        with app.app_context():
            user_1 = User.query.filter_by(email='johndoe1@example.com').first()
            self.assertIsNotNone(user_1)
            self.assertTrue(user_1.id_proof_path)
            self.assertTrue(user_1.qualification_path)

        # Test Case 2: Upload with another email
        user_data_2 = {
            'fullname': 'Jane Doe',
            'email': 'janedoe2@example.com',
            'password': 'testpassword',
            'confirm_password': 'testpassword',
            'role': 'service-provider',
            'service_type': 'cleaning',
            'location': 'Delhi',
            'hourly_rate': '45',
            'certifications': 'Certified cleaner',
            'experience': '3'
        }
        self.app.post('/register', json=user_data_2)
        
        # Simulate login for the second user
        login_response_2 = self.app.post('/login', json={'email': 'janedoe2@example.com', 'password': 'testpassword', 'role': 'service-provider'})
        login_response_json_2 = login_response_2.get_json()
        self.assertEqual(login_response_2.status_code, 200)
        self.assertEqual(login_response_json_2['status'], 'success')

        # Set the session email manually for the second user
        with self.app.session_transaction() as session:
            session['temp_email'] = 'janedoe2@example.com'

        # Upload only id proof for the second user
        files_2 = {
            'id-proof': (BytesIO(b'fake id proof content'), 'id-proof.pdf')
            
        }

        response_2 = self.app.post('/upload', data=files_2, follow_redirects=True)
        self.assertEqual(response_2.status_code, 200)
        with app.app_context():
            user_2 = User.query.filter_by(email='janedoe2@example.com').first()
            self.assertIsNotNone(user_2)
            self.assertTrue("id-proof_id-proof.pdf")    #ID proof uploaded only
            self.assertIsNone(user_2.qualification_path)

        # Test Case 3: Upload with another email (only qualification uploaded)
    
        # Register the third user
        user_data_3 = {
            'fullname': 'Alice Smith',
            'email': 'alicesmith3@example.com',
            'password': 'testpassword',
            'confirm_password': 'testpassword',
            'role': 'service-provider',
            'service_type': 'grooming',
            'location': 'Mumbai',
            'hourly_rate': '60',
            'certifications': 'Certified gardener',
            'experience': '7'
        }
        self.app.post('/register', json=user_data_3)

        # Simulate login for the third user
        login_response_3 = self.app.post(
            '/login',
            json={'email': 'alicesmith3@example.com', 'password': 'testpassword', 'role': 'service-provider'}
        )
        login_response_json_3 = login_response_3.get_json()
        self.assertEqual(login_response_3.status_code, 200)
        self.assertEqual(login_response_json_3['status'], 'success')

        # Set the session email manually for the third user
        with self.app.session_transaction() as session:
            session['temp_email'] = 'alicesmith3@example.com'

        # Upload documents for the third user (only id-proof uploaded)
        files_3 = {
            'qualification': (BytesIO(b'fake qualification content'), 'qualification.pdf')
        }

        # Post the upload request
        response_3 = self.app.post('/upload', data=files_3, content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(response_3.status_code, 200)

        # Check that the document is uploaded and saved to the database
        with app.app_context():
            user_3 = User.query.filter_by(email='alicesmith3@example.com').first()
            self.assertIsNotNone(user_3)
            self.assertIsNone(user_3.id_proof_path)
            self.assertTrue("qualification_qualification.pdf")  #qualification uploaded




    def test_login_user(self):
        """Test user login."""
        user_data = {
            'fullname': 'John Doe',
            'email': 'johndoe@example.com',
            'password': 'testpassword',
            'confirm_password': 'testpassword',
            'role': 'service-provider',
            'service_type': 'plumbing',
            'location': 'New Delhi',
            'hourly_rate': '50',
            'certifications': 'Certified groomer',
            'experience': '5'
        }
        self.app.post('/register', json=user_data)

        response = self.app.post('/login', json={'email': 'johndoe@example.com', 'password': 'testpassword', 'role': 'service-provider'})
        response_json = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'success')
        self.assertEqual(response_json['message'], 'Login successful!')
        self.assertEqual(response_json['role'], 'service-provider')
        self.assertEqual(response_json['fullname'], 'John Doe')
    def test_invalid_password(self):
        """Test login with incorrect password."""
        user_data = {
            'fullname': 'John Doe',
            'email': 'johndoe@example.com',
            'password': 'testpassword',
            'confirm_password': 'testpassword',
            'role': 'service-provider',
            'service_type': 'plumbing',
            'location': 'New Delhi',
            'hourly_rate': '50',
            'certifications': 'Certified plumber',
            'experience': '5'
        }
        self.app.post('/register', json=user_data)

        response = self.app.post('/login', json={'email': 'johndoe@example.com', 'password': 'wrongpassword', 'role': 'service-provider'})
        response_json = response.get_json()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'Invalid password!')

    def test_non_existent_email(self):
        """Test login with non-existent email."""
        response = self.app.post('/login', json={'email': 'nonexistent@example.com', 'password': 'testpassword', 'role': 'service-provider'})
        response_json = response.get_json()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'Invalid credentials or role!')

    def test_invalid_role(self):
        """Test login with incorrect role."""
        user_data = {
            'fullname': 'John Doe',
            'email': 'johndoe@example.com',
            'password': 'testpassword',
            'confirm_password': 'testpassword',
            'role': 'service-provider',
            'service_type': 'plumbing',
            'location': 'New Delhi',
            'hourly_rate': '50',
            'certifications': 'Certified plumber',
            'experience': '5'
        }
        self.app.post('/register', json=user_data)

        response = self.app.post('/login', json={'email': 'johndoe@example.com', 'password': 'testpassword', 'role': 'customer'})
        response_json = response.get_json()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'Invalid credentials or role!')

    def test_missing_email(self):
        """Test login with missing email."""
        response = self.app.post('/login', json={'password': 'testpassword', 'role': 'service-provider'})
        response_json = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'Email is required!')

    def test_missing_password(self):
        """Test login with missing password."""
        response = self.app.post('/login', json={'email': 'johndoe@example.com', 'role': 'service-provider'})
        response_json = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'Password is required!')

    def test_invalid_email_format(self):
        """Test login with invalid email format."""
        user_data = {
            'fullname': 'John Doe',
            'email': 'johndoe@example.com',
            'password': 'testpassword',
            'confirm_password': 'testpassword',
            'role': 'service-provider',
            'service_type': 'plumbing',
            'location': 'New Delhi',
            'hourly_rate': '50',
            'certifications': 'Certified plumber',
            'experience': '5'
        }
        self.app.post('/register', json=user_data)

        # Invalid email format
        response = self.app.post('/login', json={'email': 'invalid-email-format', 'password': 'testpassword', 'role': 'service-provider'})
        response_json = response.get_json()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'Invalid credentials or role!')

    def test_blank_inputs(self):
        """Test login with blank input fields."""
        response = self.app.post('/login', json={'email': '', 'password': ''})
        response_json = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'Email and password are required!')

    def test_email_with_whitespace(self):
        """Test login with email having leading or trailing whitespace."""
        user_data = {
            'fullname': 'John Doe',
            'email': 'johndoe@example.com',
            'password': 'testpassword',
            'confirm_password': 'testpassword',
            'role': 'service-provider',
            'service_type': 'plumbing',
            'location': 'New Delhi',
            'hourly_rate': '50',
            'certifications': 'Certified plumber',
            'experience': '5'
        }
        self.app.post('/register', json=user_data)

        response = self.app.post('/login', json={'email': '  johndoe@example.com  ', 'password': 'testpassword', 'role': 'service-provider'})
        response_json = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'success')
        self.assertEqual(response_json['message'], 'Login successful!')
        self.assertEqual(response_json['role'], 'service-provider')
        self.assertEqual(response_json['fullname'], 'John Doe')

    def test_forgot_password(self):
        """Test sending OTP for password reset."""
        # First, ensure the user is registered
        user_data = {
            'fullname': 'John Doe',
            'email': 'johndoe@example.com',
            'password': 'testpassword',
            'confirm_password': 'testpassword',
            'role': 'service-provider',
            'service_type': 'plumbing',
            'location': 'New Delhi',
            'hourly_rate': '50',
            'certifications': 'Certified groomer',
            'experience': '5'
        }
        self.app.post('/register', json=user_data)

        # Now request OTP for password reset
        response = self.app.post('/forgot-password', json={'email': 'johndoe@example.com'})
        response_json = response.get_json()

        self.assertEqual(response.status_code, 200, f"Failed with response: {response.data}")
        self.assertEqual(response_json['status'], 'success')
        self.assertIn('OTP sent to your email', response_json['message'])

if __name__ == '__main__':
    unittest.main()
