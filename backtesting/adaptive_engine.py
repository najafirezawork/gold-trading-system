"""
Adaptive Backtesting Engine
انتخاب خودکار بهترین استراتژی بر اساس market regime
"""

from typing import List, Dict, TYPE_CHECKING
from datetime import datetime

from data_layer.models import OHLCV, MarketData
from backtesting.models import BacktestResult
from backtesting.strategy import BaseStrategy
from backtesting.engine import BacktestEngine
from backtesting.regime_detector import MarketRegimeDetector, RegimeBasedFilter, MarketRegime

if TYPE_CHECKING:
    from agents.signal.signal_agent import SignalAgent


class AdaptiveBacktestEngine:
    """
    Engine که بر اساس market condition، استراتژی مناسب را انتخاب می‌کند
    
    Example:
        >>> strategies = {
        ...     "trending": TrendFollowingStrategy(),
        ...     "ranging": MeanReversionStrategy(),
        ... }
        >>> engine = AdaptiveBacktestEngine(strategies)
        >>> result = engine.run(data, initial_capital=10000)
    """
    
    def __init__(
        self,
        strategies: Dict[str, BaseStrategy],
        regime_detector: MarketRegimeDetector | None = None,
        regime_filter: RegimeBasedFilter | None = None,
        regime_lookback: int = 100,  # چند کندل برای تشخیص regime
        min_confidence: float = 0.6,  # حداقل confidence برای trade
        verbose: bool = True
    ):
        """
        Args:
            strategies: دیکشنری از استراتژی‌ها {name: strategy}
            regime_detector: تشخیص‌دهنده regime (اختیاری)
            regime_filter: فیلتر معاملات بر اساس regime (اختیاری)
            regime_lookback: تعداد کندل برای تشخیص regime
            min_confidence: حداقل confidence برای معامله
            verbose: نمایش لاگ‌ها
        """
        self.strategies = strategies
        self.regime_detector = regime_detector or MarketRegimeDetector()
        self.regime_filter = regime_filter or RegimeBasedFilter()
        self.regime_lookback = regime_lookback
        self.min_confidence = min_confidence
        self.verbose = verbose
        
        # آمار
        self.regime_stats: Dict[MarketRegime, int] = {
            "trending_up": 0,
            "trending_down": 0,
            "ranging": 0,
            "volatile": 0
        }
        self.strategy_usage: Dict[str, int] = {name: 0 for name in strategies.keys()}
    
    def run(
        self,
        data: List[OHLCV] | MarketData,
        initial_capital: float = 10000,
        commission: float = 2.0,
        signal_agent=None  # type: SignalAgent | None
    ) -> BacktestResult:
        """
        اجرای backtest با انتخاب خودکار استراتژی
        
        Args:
            data: داده‌های OHLCV یا MarketData
            initial_capital: سرمایه اولیه
            commission: کمیسیون هر معامله
            signal_agent: Signal Agent (اختیاری)
        
        Returns:
            BacktestResult با جزئیات کامل
        """
        # تبدیل به MarketData اگر لازم است
        if isinstance(data, list):
            market_data = MarketData(
                symbol="XAU/USD",
                interval="unknown",
                data=data
            )
        else:
            market_data = data
        
        if len(market_data.data) < self.regime_lookback:
            raise ValueError(f"Not enough data. Need at least {self.regime_lookback} candles")
        
        print(f"\n{'='*60}")
        print(f"Adaptive Backtest Engine")
        print(f"{'='*60}")
        print(f"Strategies: {', '.join(self.strategies.keys())}")
        print(f"Data: {len(market_data.data)} candles from {market_data.data[0].datetime} to {market_data.data[-1].datetime}")
        print(f"Initial Capital: ${initial_capital:,.2f}")
        print(f"Commission: ${commission:.2f} per side")
        print(f"{'='*60}\n")
        
        # ایجاد engines برای هر استراتژی
        engines = {
            name: BacktestEngine(
                strategy=strategy,
                initial_capital=initial_capital,
                commission=commission,
                use_signal_agent=(signal_agent is not None)
            )
            for name, strategy in self.strategies.items()
        }
        
        # اجرای adaptive backtest
        # به جای اجرای همه استراتژی‌ها، در هر نقطه از زمان، regime را تشخیص می‌دهیم
        # و فقط استراتژی مناسب را اجرا می‌کنیم
        
        # برای ساده‌سازی، ابتدا regime را برای کل دوره تشخیص می‌دهیم
        # سپس بهترین strategy را انتخاب و اجرا می‌کنیم
        
        # تشخیص regime برای چند نقطه مختلف
        regime_checks = []
        check_interval = len(market_data.data) // 10  # 10 نقطه برای بررسی
        
        for i in range(self.regime_lookback, len(market_data.data), check_interval):
            lookback_data = market_data.data[max(0, i - self.regime_lookback):i]
            regime_analysis = self.regime_detector.detect(lookback_data)
            regime_checks.append((i, regime_analysis))
            
            if self.verbose:
                print(f"Candle {i}: {regime_analysis.regime} "
                      f"(confidence: {regime_analysis.confidence:.1%}, "
                      f"ADX: {regime_analysis.adx:.1f}, "
                      f"volatility: {regime_analysis.volatility:.2f}%)")
        
        # آمارگیری regime ها
        for _, analysis in regime_checks:
            self.regime_stats[analysis.regime] += 1
        
        # یافتن dominant regime
        dominant_regime = max(self.regime_stats.items(), key=lambda x: x[1])[0]
        
        print(f"\nRegime Analysis:")
        print(f"Dominant regime: {dominant_regime}")
        for regime, count in self.regime_stats.items():
            pct = (count / len(regime_checks)) * 100 if regime_checks else 0
            print(f"  {regime}: {count} ({pct:.1f}%)")
        
        # اجرای همه استراتژی‌ها و انتخاب بهترین
        print(f"\nRunning strategies...\n")
        
        results = {}
        for name, engine in engines.items():
            print(f"Testing {name}...")
            result = engine.run(market_data, verbose=False)
            results[name] = result
            self.strategy_usage[name] += 1
            
            # بررسی compatibility با regime
            should_trade, reason = self.regime_filter.should_trade(
                strategy_name=name,
                regime=dominant_regime,
                confidence=regime_checks[-1][1].confidence if regime_checks else 0.5,
                min_confidence=self.min_confidence
            )
            
            compatibility = "[OK]" if should_trade else "[SKIP]"
            
            print(f"  {compatibility} {name}: "
                  f"Return: {result.total_return_pct:+.2f}%, "
                  f"Win Rate: {result.win_rate:.1f}%, "
                  f"Trades: {result.total_trades} - "
                  f"{reason}")
        
        # انتخاب بهترین استراتژی بر اساس:
        # 1. Compatibility با regime (فیلتر اول)
        # 2. Total return (معیار نهایی)
        
        compatible_results = {}
        for name, result in results.items():
            should_trade, _ = self.regime_filter.should_trade(
                strategy_name=name,
                regime=dominant_regime,
                confidence=regime_checks[-1][1].confidence if regime_checks else 0.5,
                min_confidence=self.min_confidence
            )
            if should_trade:
                compatible_results[name] = result
        
        # اگر هیچ compatible strategy نبود، همه را در نظر بگیر
        if not compatible_results:
            print(f"\nNo compatible strategies found for {dominant_regime}. Using all strategies.")
            compatible_results = results
        
        # انتخاب بهترین
        best_strategy_name = max(
            compatible_results.items(),
            key=lambda x: x[1].total_return_pct
        )[0]
        best_result = compatible_results[best_strategy_name]
        
        print(f"\n{'='*60}")
        print(f"Best Strategy: {best_strategy_name}")
        print(f"{'='*60}")
        print(f"Total Return: {best_result.total_return_pct:+.2f}%")
        print(f"Win Rate: {best_result.win_rate:.1f}%")
        print(f"Total Trades: {best_result.total_trades}")
        print(f"Sharpe Ratio: {best_result.sharpe_ratio:.2f}" if best_result.sharpe_ratio else "Sharpe Ratio: N/A")
        print(f"Max Drawdown: {best_result.max_drawdown:.2f}%")
        print(f"{'='*60}\n")
        
        return best_result
    
    def get_stats(self) -> dict:
        """آمار استفاده از strategies و regime ها"""
        return {
            "regime_distribution": self.regime_stats,
            "strategy_usage": self.strategy_usage
        }
