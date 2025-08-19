# analysis_engine.py
import pandas as pd
import numpy as np
import ccxt
from datetime import datetime, timedelta
import talib
from prophet import Prophet
import warnings
warnings.filterwarnings('ignore')

class AnalysisEngine:
    def __init__(self, api_key=None):
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'enableRateLimit': True,
        })
        
    def fetch_market_data(self, symbol, timeframe='1d', limit=100):
        """جلب بيانات السوق من البورصة"""
        ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df

    def calculate_indicators(self, df):
        """حساب المؤشرات الفنية"""
        # المتوسطات المتحركة
        df['MA20'] = talib.SMA(df['close'], timeperiod=20)
        df['MA50'] = talib.SMA(df['close'], timeperiod=50)
        
        # RSI
        df['RSI'] = talib.RSI(df['close'], timeperiod=14)
        
        # MACD
        macd, macd_signal, macd_hist = talib.MACD(df['close'], 
                                                 fastperiod=12, 
                                                 slowperiod=26, 
                                                 signalperiod=9)
        df['MACD'] = macd
        df['MACD_Signal'] = macd_signal
        df['MACD_Hist'] = macd_hist
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = talib.BBANDS(df['close'], 
                                                    timeperiod=20, 
                                                    nbdevup=2, 
                                                    nbdevdn=2)
        df['BB_Upper'] = bb_upper
        df['BB_Middle'] = bb_middle
        df['BB_Lower'] = bb_lower
        
        return df

    def generate_signals(self, df):
        """توليد إشارات تداول بناء على المؤشرات"""
        signals = []
        
        # إشارات المتوسطات المتحركة
        if df['MA20'].iloc[-1] > df['MA50'].iloc[-1]:
            signals.append("إشارة شراء: المتوسط القصير فوق المتوسط الطويل")
        else:
            signals.append("إشارة بيع: المتوسط القصير تحت المتوسط الطويل")
        
        # إشارات RSI
        if df['RSI'].iloc[-1] < 30:
            signals.append("إشارة شراء: RSI في منطقة ذروة البيع")
        elif df['RSI'].iloc[-1] > 70:
            signals.append("إشارة بيع: RSI في منطقة ذروة الشراء")
        else:
            signals.append("RSI في منطقة محايدة")
        
        # إشارات MACD
        if df['MACD'].iloc[-1] > df['MACD_Signal'].iloc[-1]:
            signals.append("إشارة شراء: MACD فوق خط الإشارة")
        else:
            signals.append("إشارة بيع: MACD تحت خط الإشارة")
            
        # إشارات Bollinger Bands
        if df['close'].iloc[-1] < df['BB_Lower'].iloc[-1]:
            signals.append("إشارة شراء: السعر تحت النطاق السفلي لبولينجر")
        elif df['close'].iloc[-1] > df['BB_Upper'].iloc[-1]:
            signals.append("إشارة بيع: السعر فوق النطاق العلوي لبولينجر")
        
        return signals

    def predict_future(self, df, periods=7):
        """التنبؤ بالسعر المستقبلي باستخدام Prophet"""
        try:
            # إعداد البيانات ل Prophet
            prophet_df = df.reset_index()[['timestamp', 'close']].rename(
                columns={'timestamp': 'ds', 'close': 'y'}
            )
            
            # تدريب النموذج
            model = Prophet(daily_seasonality=True)
            model.fit(prophet_df)
            
            # إنشاء dataframe للمستقبل
            future = model.make_future_dataframe(periods=periods)
            forecast = model.predict(future)
            
            # استخراج التنبؤات
            predictions = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods)
            
            return predictions
        except:
            # في حالة فشل Prophet نستخدم طريقة أبسط
            last_price = df['close'].iloc[-1]
            volatility = df['close'].pct_change().std()
            
            predictions = []
            for i in range(1, periods+1):
                predicted_price = last_price * (1 + np.random.normal(0, volatility))
                predictions.append({
                    'ds': datetime.now() + timedelta(days=i),
                    'yhat': predicted_price,
                    'yhat_lower': predicted_price * 0.95,
                    'yhat_upper': predicted_price * 1.05
                })
            
            return pd.DataFrame(predictions)

def analyze_symbol(symbol, api_key=None):
    """دالة رئيسية لتحليل رمز عملة"""
    engine = AnalysisEngine(api_key)
    
    # جلب البيانات
    df = engine.fetch_market_data(symbol)
    
    # حساب المؤشرات
    df = engine.calculate_indicators(df)
    
    # توليد الإشارات
    signals = engine.generate_signals(df)
    
    # التنبؤ بالمستقبل
    predictions = engine.predict_future(df)
    
    # تجهيز النتائج
    result = {
        'symbol': symbol,
        'current_price': df['close'].iloc[-1],
        'signals': signals,
        'predictions': predictions.to_dict('records'),
        'analysis_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return result

# دالة مساعدة للاستيراد من الملفات الأخرى
def fetch_market_data(symbol, timeframe='1d', limit=100):
    engine = AnalysisEngine()
    return engine.fetch_market_data(symbol, timeframe, limit)
