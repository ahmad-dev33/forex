# main.py
import threading
import time
from datetime import datetime, timedelta
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.core.window import Window
from kivy.lang import Builder

import analysis_engine as ae
import payment_system as ps
from config import API_KEY, SYMBOLS, INITIAL_BALANCE

# تحميل واجهة المستخدم من ملف kv
Builder.load_file('ui.kv')

class LoginScreen(Screen):
    status_message = StringProperty("")
    is_loading = BooleanProperty(False)

    def on_login(self):
        self.is_loading = True
        threading.Thread(target=self.verify_credentials).start()

    def verify_credentials(self):
        # محاكاة عملية التحقق
        time.sleep(2)
        
        if ps.verify_subscription():
            self.status_message = "تم التحقق من الاشتراك بنجاح!"
            Clock.schedule_once(lambda dt: self.redirect_to_main(), 2)
        else:
            self.status_message = "الاشتراك منتهي، يرجى التجديد"
            self.is_loading = False

    def redirect_to_main(self):
        self.manager.current = 'main'

class MainScreen(Screen):
    current_symbol = StringProperty("BTC/USDT")
    prediction_result = StringProperty("")
    analysis_data = StringProperty("")
    is_analyzing = BooleanProperty(False)
    balance = NumericProperty(INITIAL_BALANCE)

    def on_analyze(self):
        if not self.is_analyzing:
            self.is_analyzing = True
            threading.Thread(target=self.run_analysis).start()

    def run_analysis(self):
        try:
            # الحصول على البيانات وتحليلها
            df = ae.fetch_market_data(self.current_symbol)
            analysis_result = ae.analyze_symbol(df, self.current_symbol)
            
            # تحديث واجهة المستخدم
            Clock.schedule_once(lambda dt: self.update_analysis_result(analysis_result), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: self.show_error(str(e)), 0)
        finally:
            self.is_analyzing = False

    def update_analysis_result(self, result):
        self.analysis_data = result.get('analysis', '')
        self.prediction_result = result.get('prediction', '')
        
    def show_error(self, error_msg):
        self.analysis_data = f"خطأ: {error_msg}"
        self.prediction_result = ""

    def on_trade(self, action):
        # تنفيذ صفقة افتراضية
        if action == 'buy':
            self.balance *= 1.05  # ربح افتراضي 5%
        elif action == 'sell':
            self.balance *= 0.95  # خسارة افتراضية 5%
            
        # هنا يمكن إضافة منطق التداول الحقيقي

class PaymentScreen(Screen):
    payment_status = StringProperty("")
    payment_amount = NumericProperty(50)  # قيمة الاشتراك الشهري
    is_processing = BooleanProperty(False)

    def process_payment(self, method):
        self.is_processing = True
        threading.Thread(target=lambda: self.handle_payment(method)).start()

    def handle_payment(self, method):
        try:
            success = ps.process_payment(method, self.payment_amount)
            if success:
                self.payment_status = "تمت المعاملة بنجاح!"
                # تحديث حالة الاشتراك
                ps.update_subscription(30)  # تجديد لمدة 30 يوم
            else:
                self.payment_status = "فشلت المعاملة، يرجى المحاولة لاحقاً"
        except Exception as e:
            self.payment_status = f"خطأ: {str(e)}"
        finally:
            self.is_processing = False

class ForexCryptoApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(PaymentScreen(name='payment'))
        return sm

    def on_start(self):
        # التحقق من الاشتراك عند بدء التشغيل
        if not ps.check_subscription():
            self.root.current = 'login'

if __name__ == '__main__':
    ForexCryptoApp().run()
