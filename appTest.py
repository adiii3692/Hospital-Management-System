import pytest
from app import app, db
from werkzeug.security import generate_password_hash
import os
import tempfile

@pytest.fixture
def client():
    # Create a temporary file to use as our database
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    
    # Create the application with test config
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Create a test client
    with app.test_client() as client:
        # Create the database and tables
        with app.app_context():
            db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fname TEXT NOT NULL,
                    lname TEXT NOT NULL,
                    mail TEXT UNIQUE NOT NULL,
                    contact TEXT NOT NULL,
                    password TEXT NOT NULL,
                    hash TEXT NOT NULL,
                    gender TEXT
                )
            """)
            
            db.execute("""
                CREATE TABLE IF NOT EXISTS doctors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fname TEXT NOT NULL,
                    lname TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    hash TEXT NOT NULL
                )
            """)
            
            db.execute("""
                CREATE TABLE IF NOT EXISTS appointment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    doctor TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            yield client
    
    # Clean up
    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

def test_index_route(client):
    """Test the index route returns 200"""
    response = client.get('/')
    assert response.status_code == 200

def test_patient_registration(client):
    """Test patient registration"""
    # Test successful registration
    response = client.post('/pregister', data={
        'firstName': 'John',
        'lastName': 'Doe',
        'email': 'john@example.com',
        'contact': '1234567890',
        'password': 'password123',
        'confirmation': 'password123',
        'gender': 'Male'
    }, follow_redirects=True)
    assert response.status_code == 200
    
    # Test duplicate email registration
    response = client.post('/pregister', data={
        'firstName': 'Jane',
        'lastName': 'Doe',
        'email': 'john@example.com',
        'contact': '0987654321',
        'password': 'password123',
        'confirmation': 'password123',
        'gender': 'Female'
    })
    assert response.status_code == 403  # Should return error for duplicate email

def test_patient_login(client):
    """Test patient login"""
    # First register a patient
    client.post('/pregister', data={
        'firstName': 'John',
        'lastName': 'Doe',
        'email': 'john@example.com',
        'contact': '1234567890',
        'password': 'password123',
        'confirmation': 'password123',
        'gender': 'Male'
    })
    
    # Test successful login
    response = client.post('/plogin', data={
        'email': 'john@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    
    # Test failed login
    response = client.post('/plogin', data={
        'email': 'john@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 403

def test_doctor_login(client):
    """Test doctor login"""
    # First add a doctor through admin
    hashed = generate_password_hash('password123')
    db.execute("""
        INSERT INTO doctors (fname, lname, email, password, hash)
        VALUES (?, ?, ?, ?, ?)
    """, 'Dr.', 'Smith', 'smith@hospital.com', 'password123', hashed)
    
    # Test successful login
    response = client.post('/doctor', data={
        'email': 'smith@hospital.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    
    # Test failed login
    response = client.post('/doctor', data={
        'email': 'smith@hospital.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 403

def test_appointment_booking(client):
    """Test appointment booking"""
    # First register and login a patient
    client.post('/pregister', data={
        'firstName': 'John',
        'lastName': 'Doe',
        'email': 'john@example.com',
        'contact': '1234567890',
        'password': 'password123',
        'confirmation': 'password123',
        'gender': 'Male'
    })
    
    client.post('/plogin', data={
        'email': 'john@example.com',
        'password': 'password123'
    })
    
    # Add a doctor
    hashed = generate_password_hash('password123')
    db.execute("""
        INSERT INTO doctors (fname, lname, email, password, hash)
        VALUES (?, ?, ?, ?, ?)
    """, 'Dr.', 'Smith', 'smith@hospital.com', 'password123', hashed)
    
    # Test appointment booking
    response = client.post('/pbook', data={
        'doctor': 'Dr. Smith',
        'date': '2024-03-20',
        'time': '10:00'
    }, follow_redirects=True)
    assert response.status_code == 200
    
    # Verify appointment was created
    appointments = db.execute("SELECT * FROM appointment WHERE user_id = 1")
    assert len(appointments) == 1
    assert appointments[0]['doctor'] == 'Dr. Smith'
    assert appointments[0]['date'] == '2024-03-20'
    assert appointments[0]['time'] == '10:00'

def test_logout(client):
    """Test logout functionality"""
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200 