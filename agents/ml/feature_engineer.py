"""
Feature Engineering for ML models
استخراج ویژگی‌های تکنیکال برای مدل‌های ML
"""

from typing import List, Dict
import numpy as np
import pandas as pd
from datetime import datetime

from data_layer.models import OHLCV, MarketData


class FeatureEngineer:
    """
    ساخت features برای ML models
    
    Features شامل:
    - Technical indicators (RSI, MACD, BB, ATR)
    - Price patterns (candle patterns)
    - Statistical features (volatility, momentum)
    - Time-based features (hour, day, etc.)
    """
    
    def __init__(
        self,
        lookback_periods: List[int] = [5, 10, 20, 50],
        include_time_features: bool = True,
        include_price_patterns: bool = True
    ):
        """
        Args:
            lookback_periods: دوره‌های مختلف برای محاسبه indicators
            include_time_features: شامل کردن features زمانی
            include_price_patterns: شامل کردن الگوهای قیمتی
        """
        self.lookback_periods = lookback_periods
        self.include_time_features = include_time_features
        self.include_price_patterns = include_price_patterns
    
    def extract_features(self, market_data: MarketData) -> pd.DataFrame:
        """
        استخراج همه features از market data
        
        Returns:
            DataFrame با features و target
        """
        df = self._market_data_to_df(market_data)
        
        # Technical indicators
        df = self._add_technical_indicators(df)
        
        # Price patterns
        if self.include_price_patterns:
            df = self._add_price_patterns(df)
        
        # Microstructure features
        df = self._add_microstructure_features(df)
        
        # Multi-timeframe features
        df = self._add_multi_timeframe_features(df)
        
        # Statistical features
        df = self._add_statistical_features(df)
        
        # Time features
        if self.include_time_features:
            df = self._add_time_features(df)
        
        # Target variable (آینده قیمت - برای classification)
        df = self._add_target(df)
        
        # حذف NaN ها - فقط rows که target نداشته باشند یا خیلی NaN داشته باشند
        # Keep rows with at least 50% valid data
        threshold = len(df.columns) * 0.5
        df = df.dropna(thresh=threshold)
        
        # Fill remaining NaN با forward fill سپس 0
        df = df.ffill().fillna(0)
        
        return df
    
    def _market_data_to_df(self, market_data: MarketData) -> pd.DataFrame:
        """تبدیل MarketData به DataFrame"""
        data = {
            'datetime': [bar.datetime for bar in market_data.data],
            'open': [bar.open for bar in market_data.data],
            'high': [bar.high for bar in market_data.data],
            'low': [bar.low for bar in market_data.data],
            'close': [bar.close for bar in market_data.data],
            'volume': [bar.volume if bar.volume else 0 for bar in market_data.data]
        }
        df = pd.DataFrame(data)
        df.set_index('datetime', inplace=True)
        return df
    
    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """اضافه کردن indicators تکنیکال"""
        
        for period in self.lookback_periods:
            # Moving Averages
            df[f'sma_{period}'] = df['close'].rolling(window=period).mean()
            df[f'ema_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
            
            # Price relative to MA
            df[f'close_sma_{period}_ratio'] = df['close'] / df[f'sma_{period}']
            
            # Momentum
            df[f'momentum_{period}'] = df['close'] - df['close'].shift(period)
            df[f'roc_{period}'] = (df['close'] - df['close'].shift(period)) / df['close'].shift(period) * 100
        
        # RSI
        df['rsi_14'] = self._calculate_rsi(df['close'], 14)
        df['rsi_7'] = self._calculate_rsi(df['close'], 7)
        df['rsi_21'] = self._calculate_rsi(df['close'], 21)
        
        # MACD
        df['macd'], df['macd_signal'], df['macd_hist'] = self._calculate_macd(df['close'])
        
        # Bollinger Bands
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = self._calculate_bollinger_bands(df['close'], 20, 2)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # ATR (Average True Range)
        df['atr_14'] = self._calculate_atr(df, 14)
        df['atr_7'] = self._calculate_atr(df, 7)
        
        # Volume indicators
        df['volume_sma_20'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma_20']
        
        return df
    
    def _add_price_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """اضافه کردن الگوهای قیمتی"""
        
        # Candle body and shadows
        df['body'] = abs(df['close'] - df['open'])
        df['upper_shadow'] = df['high'] - df[['close', 'open']].max(axis=1)
        df['lower_shadow'] = df[['close', 'open']].min(axis=1) - df['low']
        df['body_ratio'] = df['body'] / (df['high'] - df['low'] + 1e-10)
        
        # Bullish/Bearish
        df['is_bullish'] = (df['close'] > df['open']).astype(int)
        
        # Doji pattern
        df['is_doji'] = (df['body'] < (df['high'] - df['low']) * 0.1).astype(int)
        
        # Hammer/Hanging Man pattern
        df['is_hammer'] = (
            (df['lower_shadow'] > df['body'] * 2) & 
            (df['upper_shadow'] < df['body'] * 0.5)
        ).astype(int)
        
        # Engulfing patterns
        df['bullish_engulfing'] = (
            (df['is_bullish'] == 1) &
            (df['is_bullish'].shift(1) == 0) &
            (df['open'] < df['close'].shift(1)) &
            (df['close'] > df['open'].shift(1))
        ).astype(int)
        
        df['bearish_engulfing'] = (
            (df['is_bullish'] == 0) &
            (df['is_bullish'].shift(1) == 1) &
            (df['open'] > df['close'].shift(1)) &
            (df['close'] < df['open'].shift(1))
        ).astype(int)
        
        return df
    
    def _add_microstructure_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """اضافه کردن ویژگی‌های ریزساختار بازار"""
        
        # Typical Price (HLC3)
        df['hlc3'] = (df['high'] + df['low'] + df['close']) / 3
        df['typical_price'] = df['hlc3']
        
        # Money Flow Index (MFI)
        df['money_flow'] = df['typical_price'] * df['volume']
        df['positive_mf'] = np.where(df['typical_price'] > df['typical_price'].shift(1), 
                                    df['money_flow'], 0)
        df['negative_mf'] = np.where(df['typical_price'] < df['typical_price'].shift(1), 
                                    df['money_flow'], 0)
        
        for period in [14, 21]:
            positive_sum = df['positive_mf'].rolling(period).sum()
            negative_sum = df['negative_mf'].rolling(period).sum()
            money_ratio = positive_sum / (negative_sum + 1e-10)  # جلوگیری از تقسیم بر صفر
            df[f'mfi_{period}'] = 100 - (100 / (1 + money_ratio))
        
        # Price-Volume Divergence
        df['pv_trend'] = df['close'].rolling(10).apply(
            lambda x: 1 if x.iloc[-1] > x.iloc[0] else -1, raw=False
        )
        df['volume_trend'] = df['volume'].rolling(10).apply(
            lambda x: 1 if x.iloc[-1] > x.iloc[0] else -1, raw=False
        )
        df['pv_divergence'] = (df['pv_trend'] != df['volume_trend']).astype(int)
        
        # Volume Price Trend (VPT)
        df['vpt'] = (df['close'].pct_change() * df['volume']).cumsum()
        df['vpt_sma_10'] = df['vpt'].rolling(10).mean()
        df['vpt_signal'] = np.where(df['vpt'] > df['vpt_sma_10'], 1, -1)
        
        # On-Balance Volume (OBV)
        df['price_change'] = df['close'].diff()
        df['obv'] = np.where(df['price_change'] > 0, df['volume'],
                    np.where(df['price_change'] < 0, -df['volume'], 0)).cumsum()
        df['obv_sma_20'] = df['obv'].rolling(20).mean()
        df['obv_signal'] = np.where(df['obv'] > df['obv_sma_20'], 1, -1)
        
        # Accumulation/Distribution Line (A/D)
        df['clv'] = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'] + 1e-10)
        df['ad_line'] = (df['clv'] * df['volume']).cumsum()
        df['ad_sma_14'] = df['ad_line'].rolling(14).mean()
        
        # Volume Rate of Change
        for period in [10, 20]:
            df[f'volume_roc_{period}'] = (df['volume'] - df['volume'].shift(period)) / (df['volume'].shift(period) + 1e-10) * 100
        
        # Price-Volume Relationship
        df['price_volume_corr_10'] = df['close'].rolling(10).corr(df['volume'])
        df['price_volume_corr_20'] = df['close'].rolling(20).corr(df['volume'])
        
        return df
    
    def _add_multi_timeframe_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """اضافه کردن ویژگی‌های چند timeframe"""
        
        # فرض: داده ورودی 1H است، 4H و 1D را شبیه‌سازی می‌کنیم
        
        # 4H timeframe simulation از 1H data
        try:
            # Resample to 4H
            df_4h = df.resample('4H', label='right').agg({
                'open': 'first',
                'high': 'max', 
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }).dropna()
            
            if len(df_4h) > 20:  # اطمینان از داشتن داده کافی
                # Calculate 4H indicators
                df_4h['rsi_4h'] = self._calculate_rsi(df_4h['close'], 14)
                df_4h['sma_20_4h'] = df_4h['close'].rolling(20).mean()
                df_4h['ema_12_4h'] = df_4h['close'].ewm(span=12, adjust=False).mean()
                df_4h['macd_4h'], _, _ = self._calculate_macd(df_4h['close'])
                df_4h['atr_4h'] = self._calculate_atr(df_4h, 14)
                
                # Bollinger Bands 4H
                df_4h['bb_upper_4h'], df_4h['bb_middle_4h'], df_4h['bb_lower_4h'] = self._calculate_bollinger_bands(df_4h['close'], 20, 2)
                df_4h['bb_position_4h'] = (df_4h['close'] - df_4h['bb_lower_4h']) / (df_4h['bb_upper_4h'] - df_4h['bb_lower_4h'] + 1e-10)
                
                # Join back to 1H (forward fill)
                df = df.join(df_4h[['rsi_4h', 'sma_20_4h', 'ema_12_4h', 'macd_4h', 'atr_4h', 
                                   'bb_upper_4h', 'bb_middle_4h', 'bb_lower_4h', 'bb_position_4h']], 
                            how='left').ffill()
        except Exception:
            # در صورت خطا، مقادیر NaN قرار می‌دهیم
            for col in ['rsi_4h', 'sma_20_4h', 'ema_12_4h', 'macd_4h', 'atr_4h', 
                       'bb_upper_4h', 'bb_middle_4h', 'bb_lower_4h', 'bb_position_4h']:
                df[col] = np.nan
        
        # Daily timeframe simulation
        try:
            df_1d = df.resample('1D', label='right').agg({
                'open': 'first',
                'high': 'max', 
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }).dropna()
            
            if len(df_1d) > 20:
                # Calculate daily indicators
                df_1d['rsi_1d'] = self._calculate_rsi(df_1d['close'], 14)
                df_1d['sma_20_1d'] = df_1d['close'].rolling(20).mean()
                df_1d['ema_12_1d'] = df_1d['close'].ewm(span=12, adjust=False).mean()
                
                # Join back to 1H
                df = df.join(df_1d[['rsi_1d', 'sma_20_1d', 'ema_12_1d']], how='left').ffill()
        except Exception:
            for col in ['rsi_1d', 'sma_20_1d', 'ema_12_1d']:
                df[col] = np.nan
        
        # Trend alignment features
        df['trend_1h'] = np.where(df['close'] > df['sma_20'], 1, -1)
        
        # 4H trend alignment
        if 'sma_20_4h' in df.columns:
            df['trend_4h'] = np.where(df['close'] > df['sma_20_4h'], 1, -1)
            df['trend_alignment_4h'] = (df['trend_1h'] == df['trend_4h']).astype(int)
        else:
            df['trend_4h'] = 0
            df['trend_alignment_4h'] = 0
        
        # Daily trend alignment
        if 'sma_20_1d' in df.columns:
            df['trend_1d'] = np.where(df['close'] > df['sma_20_1d'], 1, -1)
            df['trend_alignment_1d'] = (df['trend_1h'] == df['trend_1d']).astype(int)
            df['full_trend_alignment'] = ((df['trend_1h'] == df['trend_4h']) & 
                                         (df['trend_1h'] == df['trend_1d'])).astype(int)
        else:
            df['trend_1d'] = 0
            df['trend_alignment_1d'] = 0
            df['full_trend_alignment'] = 0
        
        # RSI divergence بین timeframes
        if 'rsi_4h' in df.columns and 'rsi_1d' in df.columns:
            df['rsi_divergence_4h'] = abs(df['rsi_14'] - df['rsi_4h'])
            df['rsi_divergence_1d'] = abs(df['rsi_14'] - df['rsi_1d'])
        else:
            df['rsi_divergence_4h'] = 0
            df['rsi_divergence_1d'] = 0
        
        # Higher timeframe momentum
        if 'ema_12_4h' in df.columns:
            df['momentum_4h'] = (df['close'] - df['ema_12_4h']) / df['ema_12_4h'] * 100
        else:
            df['momentum_4h'] = 0
            
        if 'ema_12_1d' in df.columns:
            df['momentum_1d'] = (df['close'] - df['ema_12_1d']) / df['ema_12_1d'] * 100
        else:
            df['momentum_1d'] = 0
        
        return df
    
    def _add_statistical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """اضافه کردن features آماری"""
        
        for period in [5, 10, 20]:
            # Volatility (استاندارد deviation)
            df[f'volatility_{period}'] = df['close'].rolling(window=period).std()
            
            # Price range
            df[f'high_low_range_{period}'] = (
                df['high'].rolling(window=period).max() - 
                df['low'].rolling(window=period).min()
            ) / df['close']
            
            # Returns
            df[f'returns_{period}'] = df['close'].pct_change(periods=period)
        
        # Z-score (چقدر قیمت دور از میانگین است)
        df['zscore_20'] = (df['close'] - df['close'].rolling(20).mean()) / df['close'].rolling(20).std()
        
        return df
    
    def _add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """اضافه کردن features زمانی"""
        
        # Hour of day
        df['hour'] = df.index.hour
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        
        # Day of week
        df['dayofweek'] = df.index.dayofweek
        df['is_weekend'] = (df['dayofweek'] >= 5).astype(int)
        
        # Week of month
        df['week_of_month'] = (df.index.day - 1) // 7 + 1
        
        return df
    
    def _add_target(self, df: pd.DataFrame, horizon: int = 1) -> pd.DataFrame:
        """
        اضافه کردن target variable
        
        Target: آیا قیمت در N کندل آینده بالا می‌رود؟
        0 = Down, 1 = Up
        """
        df['future_close'] = df['close'].shift(-horizon)
        df['target'] = (df['future_close'] > df['close']).astype(int)
        
        # Target برای regression (درصد تغییر)
        df['target_return'] = (df['future_close'] - df['close']) / df['close'] * 100
        
        return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """محاسبه RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(
        self, 
        prices: pd.Series, 
        fast: int = 12, 
        slow: int = 26, 
        signal: int = 9
    ) -> tuple[pd.Series, pd.Series, pd.Series]:
        """محاسبه MACD"""
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        macd_hist = macd - macd_signal
        return macd, macd_signal, macd_hist
    
    def _calculate_bollinger_bands(
        self, 
        prices: pd.Series, 
        period: int = 20, 
        num_std: float = 2.0
    ) -> tuple[pd.Series, pd.Series, pd.Series]:
        """محاسبه Bollinger Bands"""
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = middle + (std * num_std)
        lower = middle - (std * num_std)
        return upper, middle, lower
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """محاسبه Average True Range"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    def get_feature_names(self) -> List[str]:
        """لیست نام features"""
        # این را بعد از اولین extract_features صدا بزنید
        return [col for col in self._last_df.columns if col not in ['target', 'target_return', 'future_close']]
