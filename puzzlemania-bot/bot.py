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
from webdriver_manager.chrome import ChromeDriverManager

class PuzzleManiaBot:
    def __init__(self):
        self.load_config()
        self.setup_driver()
        
    def load_config(self):
        with open('config.json') as f:
            self.config = json.load(f)
        
    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"user-agent={self.config['user_agent']}")
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
    
    def generate_email(self):
        domains = ["gmail.com", "yahoo.com", "outlook.com"]
        username = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz1234567890', k=10))
        return f"{username}@{random.choice(domains)}"
    
    def register_emailoctopus(self, email):
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
            print(f"Error EmailOctopus: {str(e)}")
            return False
    
    def create_account(self, email):
        try:
            self.driver.get("https://puzzlemania.0g.ai/signup")
            
            # Isi form pendaftaran
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
            print(f"Error pendaftaran: {str(e)}")
            return False
    
    def run(self):
        success_count = 0
        
        for i in range(self.config['num_accounts']):
            print(f"\nProgress: {i+1}/{self.config['num_accounts']}")
            
            email = self.generate_email()
            print(f"Menggunakan email: {email}")
            
            if self.create_account(email):
                if self.register_emailoctopus(email):
                    success_count += 1
                    print("Akun berhasil dibuat dan didaftarkan!")
                else:
                    print("Akun dibuat tapi gagal didaftarkan ke EmailOctopus")
            else:
                print("Gagal membuat akun")
            
            # Bersihkan session
            self.driver.delete_all_cookies()
            
            # Delay antar akun
            if i < self.config['num_accounts'] - 1:
                delay = self.config['delay_between_accounts']
                print(f"Menunggu {delay} detik...")
                time.sleep(delay)
        
        print(f"\nSelesai! Total akun berhasil: {success_count}/{self.config['num_accounts']}")
        self.driver.quit()

if __name__ == "__main__":
    bot = PuzzleManiaBot()
    bot.run()