import os
import json
import random
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class PuzzleManiaBot:
    def __init__(self):
        self.load_config()
        self.setup_driver()
        
    def load_config(self):
        with open('config.json') as f:
            self.config = json.load(f)
        
    def setup_driver(self):
        """Setup Chrome WebDriver with headless options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"user-agent={self.config['user_agent']}")
        
        try:
            # Try using ChromeDriver from PATH first
            self.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"Error setting up ChromeDriver: {str(e)}")
            print("Attempting to install ChromeDriver...")
            self.install_chromedriver()
            self.driver = webdriver.Chrome(
                service=Service('/usr/local/bin/chromedriver'),
                options=chrome_options
            )
    
    def install_chromedriver(self):
        """Manually install ChromeDriver if not present"""
        if not os.path.exists("/usr/local/bin/chromedriver"):
            os.system("sudo apt-get update")
            os.system("sudo apt-get install -y wget unzip")
            os.system("wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE -O /tmp/latest_release")
            os.system("wget https://chromedriver.storage.googleapis.com/`cat /tmp/latest_release`/chromedriver_linux64.zip -O /tmp/chromedriver.zip")
            os.system("unzip /tmp/chromedriver.zip -d /tmp")
            os.system("sudo mv /tmp/chromedriver /usr/local/bin/")
            os.system("sudo chmod +x /usr/local/bin/chromedriver")
            print("ChromeDriver successfully installed")
    
    def generate_email(self):
        """Generate random email address"""
        domains = ["gmail.com", "yahoo.com", "outlook.com"]
        username = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz1234567890', k=10))
        return f"{username}@{random.choice(domains)}"
    
    def register_emailoctopus(self, email):
        """Register email with EmailOctopus"""
        url = f"https://emailoctopus.com/api/1.6/lists/{self.config['emailoctopus']['list_id']}/contacts"
        
        data = {
            'api_key': self.config['emailoctopus']['api_key'],
            'email_address': email,
            'fields': {'ReferralSource': 'PuzzleManiaBot'},
            'status': 'SUBSCRIBED'
        }
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"EmailOctopus Error: {str(e)}")
            return False
    
    def create_account(self, email):
        """Create PuzzleMania account"""
        try:
            self.driver.get("https://puzzlemania.0g.ai/signup")
            
            # Fill registration form
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            ).send_keys(email)
            
            self.driver.find_element(By.NAME, "password").send_keys(
                f"PMania{random.randint(1000,9999)}!")
            
            self.driver.find_element(By.NAME, "referralCode").send_keys(
                self.config['referral_code'])
            
            # Submit form
            self.driver.find_element(By.XPATH, "//button[contains(.,'Sign Up')]").click()
            
            time.sleep(5)
            return "dashboard" in self.driver.current_url.lower()
            
        except Exception as e:
            print(f"Registration error: {str(e)}")
            return False
    
    def run(self):
        """Main execution flow"""
        success_count = 0
        
        for i in range(self.config['num_accounts']):
            print(f"\nProgress: {i+1}/{self.config['num_accounts']}")
            
            email = self.generate_email()
            print(f"Using email: {email}")
            
            if self.create_account(email):
                if self.register_emailoctopus(email):
                    success_count += 1
                    print("Account successfully created and registered!")
                else:
                    print("Account created but failed to register with EmailOctopus")
            else:
                print("Failed to create account")
            
            # Clear session
            self.driver.delete_all_cookies()
            
            # Delay between accounts
            if i < self.config['num_accounts'] - 1:
                delay = self.config['delay_between_accounts']
                print(f"Waiting {delay} seconds...")
                time.sleep(delay)
        
        print(f"\nComplete! Total successful accounts: {success_count}/{self.config['num_accounts']}")
        self.driver.quit()

if __name__ == "__main__":
    bot = PuzzleManiaBot()
    bot.run()
