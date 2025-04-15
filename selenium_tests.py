import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import subprocess
import signal
import atexit

class HospitalManagementSystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start the Flask application in a separate process
        cls.flask_process = subprocess.Popen(
            ["python", "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for the server to start
        time.sleep(2)
        
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Initialize the Chrome WebDriver
        cls.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        cls.driver.implicitly_wait(10)
        cls.driver.get("http://127.0.0.1:5000")
        
        # Register a cleanup function to close the browser and stop the Flask server
        atexit.register(cls.tearDownClass)
    
    @classmethod
    def tearDownClass(cls):
        # Close the browser
        if hasattr(cls, 'driver'):
            cls.driver.quit()
        
        # Terminate the Flask process
        if hasattr(cls, 'flask_process'):
            cls.flask_process.terminate()
            cls.flask_process.wait()
    
    def test_home_page(self):
        """Test that the home page loads correctly"""
        self.driver.get("http://127.0.0.1:5000")
        self.assertIn("Hospital Management System", self.driver.page_source)
    
    def test_patient_registration(self):
        """Test patient registration process"""
        # Navigate to patient registration page
        self.driver.get("http://127.0.0.1:5000/pregister")
        
        # Fill in the registration form
        self.driver.find_element(By.NAME, "firstName").send_keys("John")
        self.driver.find_element(By.NAME, "lastName").send_keys("Doe")
        self.driver.find_element(By.NAME, "email").send_keys("john.doe@example.com")
        self.driver.find_element(By.NAME, "contact").send_keys("1234567890")
        self.driver.find_element(By.NAME, "password").send_keys("password123")
        self.driver.find_element(By.NAME, "confirmation").send_keys("password123")
        self.driver.find_element(By.NAME, "gender").send_keys("Male")
        
        # Submit the form
        self.driver.find_element(By.TAG_NAME, "button").click()
        
        # Check if redirected to patient dashboard
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/pdashboard")
        )
        self.assertIn("Welcome", self.driver.page_source)
    
    def test_patient_login(self):
        """Test patient login process"""
        # Navigate to patient login page
        self.driver.get("http://127.0.0.1:5000/plogin")
        
        # Fill in the login form
        self.driver.find_element(By.NAME, "email").send_keys("john.doe@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("password123")
        
        # Submit the form
        self.driver.find_element(By.TAG_NAME, "button").click()
        
        # Check if redirected to patient dashboard
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/pdashboard")
        )
        self.assertIn("Welcome", self.driver.page_source)
    
    def test_doctor_login(self):
        """Test doctor login process"""
        # Navigate to doctor login page
        self.driver.get("http://127.0.0.1:5000/doctor")
        
        # Fill in the login form
        self.driver.find_element(By.NAME, "email").send_keys("smith@hospital.com")
        self.driver.find_element(By.NAME, "password").send_keys("password123")
        
        # Submit the form
        self.driver.find_element(By.TAG_NAME, "button").click()
        
        # Check if redirected to doctor dashboard
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/ddashboard")
        )
        self.assertIn("Welcome", self.driver.page_source)
    
    def test_appointment_booking(self):
        """Test appointment booking process"""
        # First login as a patient
        self.driver.get("http://127.0.0.1:5000/plogin")
        self.driver.find_element(By.NAME, "email").send_keys("john.doe@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("password123")
        self.driver.find_element(By.TAG_NAME, "button").click()
        
        # Navigate to appointment booking page
        self.driver.get("http://127.0.0.1:5000/pbook")
        
        # Fill in the appointment form
        self.driver.find_element(By.NAME, "doctor").send_keys("Dr. Smith")
        self.driver.find_element(By.NAME, "date").send_keys("2024-03-20")
        self.driver.find_element(By.NAME, "time").send_keys("10:00")
        
        # Submit the form
        self.driver.find_element(By.TAG_NAME, "button").click()
        
        # Check if redirected back to dashboard with success message
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/pdashboard")
        )
        self.assertIn("Booked!", self.driver.page_source)
    
    def test_view_appointments(self):
        """Test viewing appointments"""
        # First login as a patient
        self.driver.get("http://127.0.0.1:5000/plogin")
        self.driver.find_element(By.NAME, "email").send_keys("john.doe@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("password123")
        self.driver.find_element(By.TAG_NAME, "button").click()
        
        # Navigate to view appointments page
        self.driver.get("http://127.0.0.1:5000/pview")
        
        # Check if appointments are displayed
        self.assertIn("Dr. Smith", self.driver.page_source)
        self.assertIn("2024-03-20", self.driver.page_source)
        self.assertIn("10:00", self.driver.page_source)
    
    def test_logout(self):
        """Test logout functionality"""
        # First login as a patient
        self.driver.get("http://127.0.0.1:5000/plogin")
        self.driver.find_element(By.NAME, "email").send_keys("john.doe@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("password123")
        self.driver.find_element(By.TAG_NAME, "button").click()
        
        # Click logout
        self.driver.get("http://127.0.0.1:5000/logout")
        
        # Check if redirected to home page
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/")
        )
        self.assertIn("Hospital Management System", self.driver.page_source)

if __name__ == "__main__":
    unittest.main() 