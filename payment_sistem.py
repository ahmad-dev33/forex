# payment_system.py
import json
import os
from datetime import datetime, timedelta
import jwt
from cryptography.fernet import Fernet

# مفاتيح التشفير (يجب تخزينها بشكل آمن في بيئة حقيقية)
KEY = Fernet.generate_key()
cipher_suite = Fernet(KEY)

class PaymentSystem:
    def __init__(self, wallet_address="YOUR_USDT_WALLET"):
        self.wallet_address = wallet_address
        self.subscription_file = "subscription_data.enc"
        
    def encrypt_data(self, data):
        """تشفير البيانات"""
        return cipher_suite.encrypt(json.dumps(data).encode())
    
    def decrypt_data(self, encrypted_data):
        """فك تشفير البيانات"""
        return json.loads(cipher_suite.decrypt(encrypted_data).decode())
    
    def check_subscription(self, user_id="default"):
        """التحقق من حالة الاشتراك"""
        try:
            if os.path.exists(self.subscription_file):
                with open(self.subscription_file, 'rb') as f:
                    encrypted_data = f.read()
                
                data = self.decrypt_data(encrypted_data)
                
                if user_id in data and data[user_id]['expiry'] > datetime.now().isoformat():
                    return True
            return False
        except:
            return False
    
    def update_subscription(self, user_id="default", days=7):
        """تحديث الاشتراك"""
        try:
            data = {}
            if os.path.exists(self.subscription_file):
                with open(self.subscription_file, 'rb') as f:
                    encrypted_data = f.read()
                data = self.decrypt_data(encrypted_data)
            
            expiry_date = datetime.now() + timedelta(days=days)
            data[user_id] = {
                'start_date': datetime.now().isoformat(),
                'expiry': expiry_date.isoformat()
            }
            
            with open(self.subscription_file, 'wb') as f:
                f.write(self.encrypt_data(data))
            
            return True
        except Exception as e:
            print(f"Error updating subscription: {e}")
            return False
    
    def process_crypto_payment(self, amount):
        """معالجة دفعة بالعملة المشفرة"""
        # في التطبيق الحقيقي، هنا نربط ببوابة الدفع
        # هذه مجرد محاكاة
        print(f"Processing crypto payment of {amount} USDT to {self.wallet_address}")
        return True
    
    def process_bank_payment(self, amount):
        """معالجة دفعة بنكية"""
        # محاكاة للدفع البنكي
        print(f"Processing bank payment of {amount}")
        return True

# دوال للاستخدام العام
def verify_subscription():
    ps = PaymentSystem()
    return ps.check_subscription()

def process_payment(method, amount):
    ps = PaymentSystem()
    if method == 'crypto':
        return ps.process_crypto_payment(amount)
    elif method == 'bank':
        return ps.process_bank_payment(amount)
    return False

def update_subscription(days):
    ps = PaymentSystem()
    return ps.update_subscription(days=days)
