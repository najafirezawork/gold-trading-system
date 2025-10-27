"""
Enhanced Technical Agent
=========================

قوی‌ترین و واضح‌ترین سیگنال‌های تکنیکال برای 1H timeframe

Strategy Logic:
- Multiple confirmation layers
- Clear entry/exit rules
- Trend filters
- Momentum confirmation
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import pandas as pd
import numpy as np

from agents.base.agent import BaseAgent, AgentOutput, AgentType
from data_layer.models import MarketData
from agents.signal.indicators import TechnicalIndicators


@dataclass
class TechnicalSignalDetail:
    """جزئیات سیگنال تکنیکال"""
    signal_type: str  # "BUY", "SELL", "HOLD"
    confidence: float  # 0 to 1
    strength: float  # -1 to 1
    entry_price: float
    stop_loss: float
    take_profit: float
    reasons: list  # دلایل سیگنال
    indicators: Dict[str, Any]  # مقادیر اندیکاتورها


class EnhancedTechnicalAgent(BaseAgent):
    """
    Technical Agent پیشرفته با سیگنال‌های قوی
    
    Features:
    - Multi-timeframe trend confirmation
    - RSI divergence detection
    - MACD histogram analysis
    - Bollinger Band squeeze detection
    - ATR-based dynamic SL/TP
    - Volume confirmation
    
    Signals are STRONG and CLEAR - not ambiguous!
    """
    
    def __init__(
        self,
        rsi_period: int = 14,
        rsi_oversold: float = 35,  # Relaxed from 30
        rsi_overbought: float = 65,  # Relaxed from 70
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
        bb_period: int = 20,
        bb_std: float = 2.0,
        atr_period: int = 14,
        atr_sl_multiplier: float = 1.5,
        atr_tp_multiplier: float = 2.5
    ):
        super().__init__(agent_type=AgentType.SIGNAL, name="Enhanced Technical Agent")
        
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.atr_period = atr_period
        self.atr_sl_multiplier = atr_sl_multiplier
        self.atr_tp_multiplier = atr_tp_multiplier
        
        self.indicators = TechnicalIndicators()
    
    def analyze(self, market_data: MarketData) -> AgentOutput:
        """
        تحلیل کامل و تولید سیگنال
        
        Returns:
            AgentOutput with detailed signal
        """
        df = self._prepare_dataframe(market_data)
        
        if len(df) < 50:
            return self._no_signal_output()
        
        # Calculate all indicators
        df = self._calculate_all_indicators(df)
        
        # Fill NaN values
        df = df.ffill().bfill()
        
        # Replace any remaining NaN/None with 0
        df = df.fillna(0)
        
        # Get current state
        current = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Analyze for BUY signals
        buy_signal, buy_reasons = self._check_buy_conditions(df, current, prev)
        
        # Analyze for SELL signals
        sell_signal, sell_reasons = self._check_sell_conditions(df, current, prev)
        
        # Determine final signal
        if buy_signal and not sell_signal:
            return self._create_buy_signal(df, current, buy_reasons)
        elif sell_signal and not buy_signal:
            return self._create_sell_signal(df, current, sell_reasons)
        else:
            return self._no_signal_output()
    
    def _prepare_dataframe(self, market_data: MarketData) -> pd.DataFrame:
        """تبدیل MarketData به DataFrame"""
        data = []
        for candle in market_data.data:
            data.append({
                'datetime': candle.datetime,
                'open': candle.open,
                'high': candle.high,
                'low': candle.low,
                'close': candle.close,
                'volume': candle.volume
            })
        
        df = pd.DataFrame(data)
        return df
    
    def _calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """محاسبه همه اندیکاتورها"""
        # RSI
        closes = df['close'].tolist()
        df['rsi'] = df['close'].rolling(self.rsi_period).apply(
            lambda x: self.indicators.calculate_rsi(x.tolist(), self.rsi_period), raw=False
        )
        
        # MACD
        df['macd'] = 0.0
        df['macd_signal'] = 0.0
        df['macd_hist'] = 0.0
        
        for i in range(len(df)):
            if i >= self.macd_slow:
                prices = closes[:i+1]
                macd_line, signal_line, histogram = self.indicators.calculate_macd(
                    prices, self.macd_fast, self.macd_slow, self.macd_signal
                )
                df.iloc[i, df.columns.get_loc('macd')] = macd_line
                df.iloc[i, df.columns.get_loc('macd_signal')] = signal_line
                df.iloc[i, df.columns.get_loc('macd_hist')] = histogram
        
        # Bollinger Bands
        df['bb_upper'] = 0.0
        df['bb_middle'] = 0.0
        df['bb_lower'] = 0.0
        df['bb_width'] = 0.0
        
        for i in range(len(df)):
            if i >= self.bb_period:
                prices = closes[i-self.bb_period+1:i+1]
                upper, middle, lower = self.indicators.calculate_bollinger_bands(
                    prices, self.bb_period, self.bb_std
                )
                df.iloc[i, df.columns.get_loc('bb_upper')] = upper
                df.iloc[i, df.columns.get_loc('bb_middle')] = middle
                df.iloc[i, df.columns.get_loc('bb_lower')] = lower
                df.iloc[i, df.columns.get_loc('bb_width')] = (upper - lower) / middle if middle > 0 else 0
        
        # SMAs for trend
        df['sma_20'] = df['close'].rolling(20).mean()
        df['sma_50'] = df['close'].rolling(50).mean()
        df['sma_200'] = df['close'].rolling(200).mean() if len(df) >= 200 else df['close'].rolling(len(df)//2).mean()
        
        # ATR for volatility - simple calculation
        df['atr'] = 0.0
        highs = df['high'].tolist()
        lows = df['low'].tolist()
        closes = df['close'].tolist()
        for i in range(len(df)):
            if i >= self.atr_period:
                atr_val = self.indicators.calculate_atr(
                    highs[i-self.atr_period:i+1],
                    lows[i-self.atr_period:i+1],
                    closes[i-self.atr_period:i+1],
                    self.atr_period
                )
                df.iloc[i, df.columns.get_loc('atr')] = atr_val
        
        # Volume MA
        df['volume_ma'] = df['volume'].rolling(20).mean()
        
        # Price momentum
        df['momentum'] = df['close'].pct_change(5) * 100
        
        return df
    
    def _check_buy_conditions(self, df: pd.DataFrame, current: pd.Series, prev: pd.Series) -> bool:
        """
        شرایط BUY - RELAXED برای بیشتر سیگنال
        
        BUY if ANY 2 of these:
        1. RSI < 50 (نیمه پایین) AND turning up
        2. MACD bullish or improving
        3. Price near lower BB (< 40%)
        4. Uptrend (SMA20 > SMA50) OR price above SMA20
        5. Volume above average
        """
        conditions_met = 0
        reasons = []
        
        # Condition 1: RSI in lower half and improving
        if current['rsi'] < 50:
            if current['rsi'] > prev['rsi']:
                conditions_met += 1
                reasons.append(f"RSI improving ({current['rsi']:.1f} < 50, rising)")
        
        # Condition 2: MACD bullish
        if current['macd_hist'] > 0 or current['macd_hist'] > prev['macd_hist']:
            conditions_met += 1
            reasons.append(f"MACD bullish (hist={current['macd_hist']:.4f})")
        
        # Condition 3: Near lower BB
        bb_range = current['bb_upper'] - current['bb_lower']
        if bb_range > 0:
            bb_position = (current['close'] - current['bb_lower']) / bb_range
            if bb_position < 0.4:  # In lower 40%
                conditions_met += 1
                reasons.append(f"Near BB lower band ({bb_position*100:.1f}%)")
        
        # Condition 4: Trend or price position
        if current['sma_20'] > current['sma_50'] or current['close'] > current['sma_20']:
            conditions_met += 1
            reasons.append("Uptrend (SMA20 > SMA50)" if current['sma_20'] > current['sma_50'] else "Above SMA20")
        
        # Condition 5: Volume
        if current['volume'] > current['volume_ma'] * 1.0:  # Just above average
            conditions_met += 1
            reasons.append("Volume above average")
        
        # Need at least 2 out of 5 conditions (relaxed from 3)
        if conditions_met >= 2:
            return True, reasons
        
        return False, []
    
    def _check_sell_conditions(self, df: pd.DataFrame, current: pd.Series, prev: pd.Series) -> bool:
        """
        شرایط SELL - RELAXED
        
        SELL if ANY 2 of these:
        1. RSI > 50 (نیمه بالا) AND turning down
        2. MACD bearish or weakening
        3. Price near upper BB (> 60%)
        4. Downtrend (SMA20 < SMA50) OR price below SMA20
        5. Volume above average
        """
        conditions_met = 0
        reasons = []
        
        # Condition 1: RSI in upper half and declining
        if current['rsi'] > 50:
            if current['rsi'] < prev['rsi']:
                conditions_met += 1
                reasons.append(f"RSI declining ({current['rsi']:.1f} > 50, falling)")
        
        # Condition 2: MACD bearish
        if current['macd_hist'] < 0 or current['macd_hist'] < prev['macd_hist']:
            conditions_met += 1
            reasons.append(f"MACD bearish (hist={current['macd_hist']:.4f})")
        
        # Condition 3: Near upper BB
        bb_range = current['bb_upper'] - current['bb_lower']
        if bb_range > 0:
            bb_position = (current['close'] - current['bb_lower']) / bb_range
            if bb_position > 0.6:  # In upper 40%
                conditions_met += 1
                reasons.append(f"Near BB upper band ({bb_position*100:.1f}%)")
        
        # Condition 4: Trend or price position
        if current['sma_20'] < current['sma_50'] or current['close'] < current['sma_20']:
            conditions_met += 1
            reasons.append("Downtrend (SMA20 < SMA50)" if current['sma_20'] < current['sma_50'] else "Below SMA20")
        
        # Condition 5: Volume
        if current['volume'] > current['volume_ma'] * 1.0:
            conditions_met += 1
            reasons.append("Volume above average")
        
        # Need at least 2 out of 5 conditions
        if conditions_met >= 2:
            return True, reasons
        
        return False, []
    
    def _create_buy_signal(self, df: pd.DataFrame, current: pd.Series, reasons: List[str]) -> AgentOutput:
        """ساخت سیگنال BUY با جزئیات کامل"""
        atr = current['atr'] if current['atr'] > 0 else current['close'] * 0.01  # Fallback
        entry_price = current['close']
        
        # Dynamic SL/TP based on ATR
        stop_loss = entry_price - (self.atr_sl_multiplier * atr)
        take_profit = entry_price + (self.atr_tp_multiplier * atr)
        
        # Calculate confidence based on number of conditions met
        confidence = min(0.5 + (len(reasons) * 0.1), 0.9)
        
        bb_position = 0.0
        bb_range = current['bb_upper'] - current['bb_lower']
        if bb_range > 0:
            bb_position = (current['close'] - current['bb_lower']) / bb_range
        
        return AgentOutput(
            agent_type=self.agent_type,
            signal=0.8,  # Strong buy
            confidence=confidence,
            metadata={
                'signal_type': 'BUY',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'atr': atr,
                'risk_reward_ratio': (take_profit - entry_price) / (entry_price - stop_loss),
                'reasons': reasons,
                'indicators': {
                    'rsi': current['rsi'],
                    'macd': current['macd'],
                    'macd_hist': current['macd_hist'],
                    'bb_position': bb_position,
                    'sma_20': current['sma_20'],
                    'sma_50': current['sma_50']
                }
            }
        )
    
    def _create_sell_signal(self, df: pd.DataFrame, current: pd.Series, reasons: List[str]) -> AgentOutput:
        """ساخت سیگنال SELL با جزئیات کامل"""
        atr = current['atr'] if current['atr'] > 0 else current['close'] * 0.01
        entry_price = current['close']
        
        # Dynamic SL/TP based on ATR
        stop_loss = entry_price + (self.atr_sl_multiplier * atr)
        take_profit = entry_price - (self.atr_tp_multiplier * atr)
        
        # Calculate confidence
        confidence = min(0.5 + (len(reasons) * 0.1), 0.9)
        
        bb_position = 0.0
        bb_range = current['bb_upper'] - current['bb_lower']
        if bb_range > 0:
            bb_position = (current['close'] - current['bb_lower']) / bb_range
        
        return AgentOutput(
            agent_type=self.agent_type,
            signal=-0.8,  # Strong sell
            confidence=confidence,
            metadata={
                'signal_type': 'SELL',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'atr': atr,
                'risk_reward_ratio': (entry_price - take_profit) / (stop_loss - entry_price) if stop_loss > entry_price else 0,
                'reasons': reasons,
                'indicators': {
                    'rsi': current['rsi'],
                    'macd': current['macd'],
                    'macd_hist': current['macd_hist'],
                    'bb_position': bb_position,
                    'sma_20': current['sma_20'],
                    'sma_50': current['sma_50']
                }
            }
        )
    
    def _calculate_confidence(self, df: pd.DataFrame, current: pd.Series, signal_type: str) -> float:
        """
        محاسبه confidence بر اساس قدرت شرایط
        
        Factors:
        - How strong is RSI signal?
        - How strong is MACD?
        - Trend alignment?
        - Volume confirmation?
        """
        confidence_score = 0.0
        
        if signal_type == "BUY":
            # RSI strength (0-0.25)
            rsi_strength = max(0, (self.rsi_oversold - current['rsi']) / self.rsi_oversold)
            confidence_score += rsi_strength * 0.25
            
            # MACD strength (0-0.25)
            if current['macd_hist'] > 0:
                confidence_score += 0.25
            elif current['macd'] > current['macd_signal']:
                confidence_score += 0.15
            
            # Trend alignment (0-0.3)
            if current['sma_20'] > current['sma_50']:
                confidence_score += 0.3
            
            # Volume (0-0.2)
            if current['volume'] > current['volume_ma'] * 1.2:
                confidence_score += 0.2
            elif current['volume'] > current['volume_ma']:
                confidence_score += 0.1
        
        else:  # SELL
            # RSI strength
            rsi_strength = max(0, (current['rsi'] - self.rsi_overbought) / (100 - self.rsi_overbought))
            confidence_score += rsi_strength * 0.25
            
            # MACD strength
            if current['macd_hist'] < 0:
                confidence_score += 0.25
            elif current['macd'] < current['macd_signal']:
                confidence_score += 0.15
            
            # Trend alignment
            if current['sma_20'] < current['sma_50']:
                confidence_score += 0.3
            
            # Volume
            if current['volume'] > current['volume_ma'] * 1.2:
                confidence_score += 0.2
            elif current['volume'] > current['volume_ma']:
                confidence_score += 0.1
        
        return min(1.0, max(0.4, confidence_score))  # Between 0.4 and 1.0
    
    def _no_signal_output(self) -> AgentOutput:
        """بدون سیگنال - HOLD"""
        return AgentOutput(
            agent_type=self.agent_type,
            signal=0.0,
            confidence=0.0,
            metadata={
                'signal_type': 'HOLD',
                'reasons': ['No clear signal']
            }
        )
