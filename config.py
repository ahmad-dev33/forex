# config.py
import os
from dotenv import load_dotenv

# تحميل المتغيرات من ملف البيئة
load_dotenv()

# إعدادات التطبيق
API_KEY = os.getenv('API_KEY', 'your_api_key_here')
INITIAL_BALANCE = 10000  # رصيد ابتدائي افتراضي

# قائمة الرموز المدعومة
SYMBOLS = [
    "BTC/USDT", "ETH/USDT", "XRP/USDT", "LTC/USDT", "BCH/USDT",
    "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD"
]

# إعدادات الأمان
JWT_SECRET = os.getenv('JWT_SECRET', 'your_jwt_secret_here')
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'your_encryption_key_here')

# إعدادات البوابة المالية
CRYPTO_WALLET = os.getenv('CRYPTO_WALLET', 'your_usdt_wallet_address')
BANK_GATEWAY_URL = os.getenv('BANK_GATEWAY_URL', 'https://payment-gateway.com')
