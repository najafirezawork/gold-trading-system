"""
Risk Management Agent
======================

مسئولیت‌ها:
1. محاسبه position size بر اساس ATR و ریسک
2. تایید/رد معامله بر اساس محدودیت‌های ریسک
3. مدیریت drawdown و circuit breakers
4. محدودیت تعداد معاملات همزمان و روزانه

این agent می‌تواند هر معامله‌ای رو VETO کنه اگه ریسک زیاد باشه!
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np

from agents.base.agent import BaseAgent, AgentOutput, AgentType
from data_layer.models import MarketData


@dataclass
class RiskAssessment:
    """ارزیابی ریسک یک معامله"""
    approved: bool
    position_size: float  # In units
    risk_amount: float  # In currency
    stop_loss_price: float
    take_profit_price: float
    risk_reward_ratio: float
    rejection_reasons: List[str]
    warnings: List[str]


class RiskManagementAgent(BaseAgent):
    """
    Agent مدیریت ریسک
    
    Features:
    - ATR-based position sizing
    - Max risk per trade (default 1%)
    - Max portfolio drawdown protection (default 8%)
    - Max concurrent trades (default 1)
    - Max daily trades (default 3)
    - Circuit breaker on daily loss limit (default 3%)
    """
    
    def __init__(
        self,
        account_balance: float = 10000.0,
        max_risk_per_trade_pct: float = 1.0,
        max_portfolio_drawdown_pct: float = 8.0,
        max_concurrent_trades: int = 1,
        max_daily_trades: int = 3,
        daily_loss_limit_pct: float = 3.0,
        min_risk_reward: float = 1.5
    ):
        super().__init__(agent_type=AgentType.RISK, name="Risk Management")
        
        # Account settings
        self.account_balance = account_balance
        self.current_balance = account_balance
        self.peak_balance = account_balance
        
        # Risk parameters
        self.max_risk_per_trade_pct = max_risk_per_trade_pct
        self.max_portfolio_drawdown_pct = max_portfolio_drawdown_pct
        self.max_concurrent_trades = max_concurrent_trades
        self.max_daily_trades = max_daily_trades
        self.daily_loss_limit_pct = daily_loss_limit_pct
        self.min_risk_reward = min_risk_reward
        
        # Trade tracking
        self.open_positions: List[Dict] = []
        self.daily_trades: Dict[str, int] = {}  # date -> count
        self.daily_pnl: Dict[str, float] = {}  # date -> P&L
    
    def analyze(
        self,
        market_data: MarketData,
        signal_output: AgentOutput,
        stop_loss: float,
        take_profit: float
    ) -> AgentOutput:
        """
        ارزیابی ریسک و تایید/رد معامله
        
        Args:
            market_data: داده‌های بازار
            signal_output: سیگنال از agents قبلی
            stop_loss: قیمت stop loss پیشنهادی
            take_profit: قیمت take profit پیشنهادی
        
        Returns:
            AgentOutput with approval and position sizing
        """
        current_price = market_data.data[-1].close
        
        # اگر سیگنال neutral بود، رد کن
        if abs(signal_output.signal) < 0.1:
            return self._reject_trade(
                signal_output,
                reasons=["No signal - neutral"],
                warnings=[]
            )
        
        # بررسی محدودیت‌های کلی
        rejection_reasons, warnings = self._check_constraints(market_data)
        
        if rejection_reasons:
            return self._reject_trade(signal_output, rejection_reasons, warnings)
        
        # محاسبه position size
        risk_assessment = self._calculate_position_size(
            current_price=current_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            signal_direction=1 if signal_output.signal > 0 else -1
        )
        
        # بررسی risk/reward
        if risk_assessment.risk_reward_ratio < self.min_risk_reward:
            rejection_reasons.append(
                f"Poor R/R ratio {risk_assessment.risk_reward_ratio:.2f} < {self.min_risk_reward}"
            )
        
        # تصمیم نهایی
        if rejection_reasons or not risk_assessment.approved:
            return self._reject_trade(
                signal_output,
                rejection_reasons + risk_assessment.rejection_reasons,
                warnings + risk_assessment.warnings
            )
        
        # تایید معامله
        return self._approve_trade(signal_output, risk_assessment, warnings)
    
    def _check_constraints(self, market_data: MarketData) -> tuple[List[str], List[str]]:
        """بررسی محدودیت‌های کلی"""
        rejection_reasons = []
        warnings = []
        
        # 1. Check portfolio drawdown
        current_drawdown = self._calculate_current_drawdown()
        if current_drawdown >= self.max_portfolio_drawdown_pct:
            rejection_reasons.append(
                f"Max drawdown exceeded: {current_drawdown:.1f}% >= {self.max_portfolio_drawdown_pct}%"
            )
        elif current_drawdown >= self.max_portfolio_drawdown_pct * 0.8:
            warnings.append(
                f"Warning: High drawdown {current_drawdown:.1f}%"
            )
        
        # 2. Check concurrent trades
        if len(self.open_positions) >= self.max_concurrent_trades:
            rejection_reasons.append(
                f"Max concurrent trades reached: {len(self.open_positions)}"
            )
        
        # 3. Check daily trade limit
        today = datetime.now().strftime('%Y-%m-%d')
        daily_count = self.daily_trades.get(today, 0)
        if daily_count >= self.max_daily_trades:
            rejection_reasons.append(
                f"Daily trade limit reached: {daily_count}/{self.max_daily_trades}"
            )
        
        # 4. Check daily loss limit (circuit breaker)
        daily_loss_pct = abs(self.daily_pnl.get(today, 0.0)) / self.account_balance * 100
        if daily_loss_pct >= self.daily_loss_limit_pct:
            rejection_reasons.append(
                f"Daily loss limit hit: {daily_loss_pct:.1f}% >= {self.daily_loss_limit_pct}%"
            )
        
        return rejection_reasons, warnings
    
    def _calculate_position_size(
        self,
        current_price: float,
        stop_loss: float,
        take_profit: float,
        signal_direction: int
    ) -> RiskAssessment:
        """
        محاسبه position size بر اساس ATR و ریسک
        
        Formula:
        Position Size = (Account Balance × Risk%) / (Stop Loss Distance)
        """
        rejection_reasons = []
        warnings = []
        
        # محاسبه ریسک per trade
        risk_amount = self.current_balance * (self.max_risk_per_trade_pct / 100)
        
        # محاسبه فاصله SL و TP
        if signal_direction > 0:  # BUY
            sl_distance = current_price - stop_loss
            tp_distance = take_profit - current_price
        else:  # SELL
            sl_distance = stop_loss - current_price
            tp_distance = current_price - take_profit
        
        # بررسی صحت SL و TP
        if sl_distance <= 0:
            rejection_reasons.append("Invalid stop loss - must be below current price for BUY")
        if tp_distance <= 0:
            rejection_reasons.append("Invalid take profit - must be above current price for BUY")
        
        if rejection_reasons:
            return RiskAssessment(
                approved=False,
                position_size=0,
                risk_amount=0,
                stop_loss_price=stop_loss,
                take_profit_price=take_profit,
                risk_reward_ratio=0,
                rejection_reasons=rejection_reasons,
                warnings=warnings
            )
        
        # محاسبه position size
        position_size = risk_amount / sl_distance
        
        # محاسبه risk/reward ratio
        rr_ratio = tp_distance / sl_distance if sl_distance > 0 else 0
        
        # بررسی حداقل position size
        if position_size < 0.01:
            warnings.append(f"Very small position size: {position_size:.4f}")
        
        # بررسی حداکثر position size (max 10% of balance)
        max_position_value = self.current_balance * 0.1
        if position_size * current_price > max_position_value:
            warnings.append(
                f"Position size limited to 10% of balance: {position_size:.4f} -> {max_position_value/current_price:.4f}"
            )
            position_size = max_position_value / current_price
        
        return RiskAssessment(
            approved=True,
            position_size=position_size,
            risk_amount=risk_amount,
            stop_loss_price=stop_loss,
            take_profit_price=take_profit,
            risk_reward_ratio=rr_ratio,
            rejection_reasons=rejection_reasons,
            warnings=warnings
        )
    
    def _calculate_current_drawdown(self) -> float:
        """محاسبه drawdown فعلی"""
        if self.peak_balance == 0:
            return 0.0
        
        drawdown = (self.peak_balance - self.current_balance) / self.peak_balance * 100
        return max(0.0, drawdown)
    
    def _approve_trade(
        self,
        signal_output: AgentOutput,
        risk_assessment: RiskAssessment,
        warnings: List[str]
    ) -> AgentOutput:
        """تایید معامله"""
        
        # محاسبه confidence بر اساس risk metrics
        confidence = signal_output.confidence
        
        # کاهش confidence برای هشدارها
        if warnings:
            confidence *= 0.9
        
        # کاهش confidence برای risk/reward پایین
        if risk_assessment.risk_reward_ratio < 2.0:
            confidence *= 0.95
        
        return AgentOutput(
            agent_type=self.agent_type,
            signal=signal_output.signal,
            confidence=confidence,
            metadata={
                'risk_decision': 'APPROVED',
                'position_size': risk_assessment.position_size,
                'risk_amount': risk_assessment.risk_amount,
                'stop_loss': risk_assessment.stop_loss_price,
                'take_profit': risk_assessment.take_profit_price,
                'risk_reward_ratio': risk_assessment.risk_reward_ratio,
                'warnings': warnings,
                'current_balance': self.current_balance,
                'current_drawdown_pct': self._calculate_current_drawdown(),
                'open_positions_count': len(self.open_positions),
                'original_signal': signal_output.metadata
            }
        )
    
    def _reject_trade(
        self,
        signal_output: AgentOutput,
        reasons: List[str],
        warnings: List[str]
    ) -> AgentOutput:
        """رد معامله"""
        return AgentOutput(
            agent_type=self.agent_type,
            signal=0.0,  # Neutralize signal
            confidence=0.9,  # High confidence in rejection
            metadata={
                'risk_decision': 'REJECTED',
                'rejection_reasons': reasons,
                'warnings': warnings,
                'current_balance': self.current_balance,
                'current_drawdown_pct': self._calculate_current_drawdown(),
                'original_signal': signal_output.signal
            }
        )
    
    def update_balance(self, new_balance: float):
        """Update current balance and peak"""
        self.current_balance = new_balance
        if new_balance > self.peak_balance:
            self.peak_balance = new_balance
    
    def record_trade(self, pnl: float, timestamp: datetime):
        """Record completed trade"""
        date_str = timestamp.strftime('%Y-%m-%d')
        
        # Update daily trades count
        self.daily_trades[date_str] = self.daily_trades.get(date_str, 0) + 1
        
        # Update daily P&L
        self.daily_pnl[date_str] = self.daily_pnl.get(date_str, 0.0) + pnl
        
        # Update balance
        self.update_balance(self.current_balance + pnl)
