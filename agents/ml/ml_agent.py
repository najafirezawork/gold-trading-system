"""
ML Agent - Machine Learning Agent for predictive analytics
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
import pandas as pd
import numpy as np
from pathlib import Path

from agents.base import BaseAgent, AgentOutput, AgentType
from agents.ml.feature_engineer import FeatureEngineer
from agents.ml.feature_selector import AdvancedFeatureSelector
from agents.ml.models import MLModel, RandomForestModel, XGBoostModel, EnsembleModel
from data_layer.models import MarketData


@dataclass
class MLAgentOutput:
    """
    Output from ML Agent - Continuous Signal Generator
    
    ML Agent تولید می‌کند:
    - prob_up: احتمال حرکت صعودی (0-1)
    - prob_down: احتمال حرکت نزولی (0-1)
    - trend_strength: قدرت ترند (0-1)
    - volatility: نوسان‌پذیری بازار (0-1)
    - momentum: مومنتوم بازار (-1 to +1)
    
    هیچ BUY/SELL/HOLD اینجا وجود ندارد!
    تصمیم‌گیری با Decision Agent است.
    """
    prob_up: float  # احتمال حرکت صعودی (0-1)
    prob_down: float  # احتمال حرکت نزولی (0-1)
    trend_strength: float  # قدرت ترند (0-1)
    volatility: float  # نوسان‌پذیری (0-1)
    momentum: float  # مومنتوم (-1 to +1)
    metadata: Dict[str, Any]


class MLAgent(BaseAgent):
    """
    ML Agent - Continuous Signal Generator
    
    🎯 نقش: تولید سیگنال‌های مداوم (Continuous Signals) از market data
    
    ❌ این Agent تصمیم‌گیری نمی‌کند (No BUY/SELL/HOLD)
    ✅ فقط احتمالات و قدرت‌ها را محاسبه می‌کند
    
    خروجی:
    {
        "prob_up": 0.34,
        "prob_down": 0.66,
        "trend_strength": 0.61,
        "volatility": 0.87,
        "momentum": -0.32
    }
    
    Features:
    - Feature engineering از market data
    - Probability prediction (نه classification)
    - Trend strength calculation
    - Volatility estimation
    - Momentum analysis
    
    Example:
        >>> agent = MLAgent()
        >>> agent.train(train_data)
        >>> signal = agent.analyze(test_data)
        >>> print(f"UP Probability: {signal.prob_up:.2%}")
        >>> print(f"Trend Strength: {signal.trend_strength:.2%}")
    """
    
    def __init__(
        self,
        feature_engineer: Optional[FeatureEngineer] = None,
        feature_selector: Optional[AdvancedFeatureSelector] = None,
        model: Optional[MLModel] = None,
        model_path: Optional[str] = None,
        enable_feature_selection: bool = True
    ):
        """
        Args:
            feature_engineer: FeatureEngineer instance (اختیاری)
            feature_selector: AdvancedFeatureSelector instance (اختیاری)
            model: MLModel instance (اختیاری، default: Ensemble)
            model_path: مسیر برای save/load model
            enable_feature_selection: فعال‌سازی feature selection اتوماتیک
        """
        super().__init__(agent_type=AgentType.ML, name="ML Signal Generator")
        
        self.feature_engineer = feature_engineer or FeatureEngineer()
        self.feature_selector = feature_selector or AdvancedFeatureSelector(n_features=25)
        self.enable_feature_selection = enable_feature_selection
        
        # اگر model داده نشد، Ensemble بساز
        if model is None:
            self.model = EnsembleModel([
                RandomForestModel(n_estimators=100, max_depth=10),
                XGBoostModel(n_estimators=100, max_depth=6, learning_rate=0.1)
            ])
        else:
            self.model = model
        
        self.model_path = model_path or "models/ml_agent_model.pkl"
        
        # آمار
        self.training_history: List[Dict] = []
        self.last_features: Optional[pd.DataFrame] = None
        self.selected_features: Optional[List[str]] = None
    
    def train(
        self,
        market_data: MarketData,
        val_split: float = 0.2,
        save_model: bool = True
    ) -> Dict[str, Any]:
        """
        Train the ML model
        
        Args:
            market_data: داده‌های تاریخی
            val_split: درصد validation set
            save_model: ذخیره model بعد از training
        
        Returns:
            Training metrics
        """
        print(f"\n{'='*60}")
        print(f"Training ML Agent")
        print(f"{'='*60}")
        print(f"Data: {len(market_data)} candles")
        print(f"Validation split: {val_split:.1%}")
        
        # Feature extraction
        print(f"\nExtracting features...")
        df = self.feature_engineer.extract_features(market_data)
        
        print(f"Features extracted: {len(df)} samples, {len(df.columns)-2} features")
        
        # Split features and target
        feature_cols = [col for col in df.columns if col not in ['target', 'target_return', 'future_close']]
        X = df[feature_cols]
        y = df['target']
        
        # Feature Selection
        if self.enable_feature_selection:
            print(f"\nPerforming feature selection...")
            X_selected = self.feature_selector.select_features(X, y, method='combined')
            self.selected_features = list(X_selected.columns)
            
            # Get selection report
            selection_report = self.feature_selector.get_selection_report()
            print(f"Selected {len(self.selected_features)} features out of {len(X.columns)}")
            print(f"Top features: {[f[0] for f in selection_report.get('top_features', [])[:5]]}")
            
            X = X_selected
        else:
            self.selected_features = list(X.columns)
        
        # Train/Val split
        split_idx = int(len(X) * (1 - val_split))
        
        X_train = X.iloc[:split_idx]
        y_train = y.iloc[:split_idx]
        X_val = X.iloc[split_idx:]
        y_val = y.iloc[split_idx:]
        
        print(f"\nTrain samples: {len(X_train)}")
        print(f"Validation samples: {len(X_val)}")
        print(f"Class distribution (train): UP={sum(y_train)}, DOWN={len(y_train)-sum(y_train)}")
        
        # Train model
        print(f"\nTraining {self.model.name} model...")
        metrics = self.model.train(X_train, y_train, X_val, y_val)
        
        # نمایش metrics
        print(f"\n{'='*60}")
        print(f"Training Results:")
        print(f"{'='*60}")
        
        for key, value in metrics.items():
            if isinstance(value, dict):
                print(f"\n{key}:")
                for k, v in value.items():
                    print(f"  {k}: {v:.4f}")
            else:
                print(f"{key}: {value:.4f}")
        
        # Feature importance
        importance = self.model.get_feature_importance()
        if importance:
            print(f"\nTop 10 Important Features:")
            sorted_importance = sorted(importance.items(), key=lambda x: x[1], reverse=True)
            for i, (feature, score) in enumerate(sorted_importance[:10], 1):
                print(f"  {i}. {feature}: {score:.4f}")
        
        # ذخیره history
        self.training_history.append({
            'timestamp': datetime.now(),
            'samples': len(X_train),
            'metrics': metrics
        })
        
        # Save model
        if save_model:
            print(f"\nSaving model to {self.model_path}...")
            self.model.save(self.model_path)
            print(f"Model saved successfully!")
        
        print(f"{'='*60}\n")
        
        return metrics
    
    def analyze(self, market_data: MarketData) -> MLAgentOutput:
        """
        تولید سیگنال‌های مداوم از market data
        
        🎯 خروجی: Continuous Signals (نه Classification!)
        
        Returns:
            MLAgentOutput با:
            - prob_up: احتمال صعودی
            - prob_down: احتمال نزولی
            - trend_strength: قدرت ترند
            - volatility: نوسان
            - momentum: مومنتوم
        """
        if not self.model.is_trained:
            # سعی کن model را load کنی
            if Path(self.model_path).exists():
                print(f"Loading model from {self.model_path}...")
                self.model.load(self.model_path)
            else:
                raise ValueError("Model not trained! Call train() first or provide a trained model path.")
        
        # Feature extraction
        df = self.feature_engineer.extract_features(market_data)
        
        # آخرین row (current state)
        feature_cols = [col for col in df.columns if col not in ['target', 'target_return', 'future_close']]
        current_features = df[feature_cols].iloc[[-1]]
        
        # اگر feature selection استفاده شده، فقط selected features را بگیر
        if self.enable_feature_selection and self.selected_features:
            # اطمینان از اینکه features موجود هستند
            available_features = [f for f in self.selected_features if f in current_features.columns]
            if len(available_features) > 0:
                current_features = current_features[available_features]
            else:
                print("⚠️ Warning: No selected features found in current data, using all features")
        
        self.last_features = current_features
        
        # ========================================
        # 1️⃣ Probability Prediction (نه Classification!)
        # ========================================
        proba = self.model.predict_proba(current_features)[0]  # [P(DOWN), P(UP)]
        
        prob_down = float(proba[0])
        prob_up = float(proba[1])
        
        # ========================================
        # 2️⃣ Trend Strength از features
        # ========================================
        # استفاده از ADX یا SMA slopes
        if 'adx_14' in df.columns:
            trend_strength = float(min(df['adx_14'].iloc[-1] / 100.0, 1.0))
        else:
            # fallback: از تفاوت SMA‌ها
            if 'sma_20' in df.columns and 'sma_50' in df.columns:
                sma_diff = abs(df['sma_20'].iloc[-1] - df['sma_50'].iloc[-1])
                sma_avg = (df['sma_20'].iloc[-1] + df['sma_50'].iloc[-1]) / 2
                trend_strength = float(min(sma_diff / sma_avg, 1.0))
            else:
                trend_strength = 0.5  # default
        
        # ========================================
        # 3️⃣ Volatility از ATR
        # ========================================
        if 'atr_14' in df.columns:
            current_price = float(market_data.data[-1].close)
            atr = float(df['atr_14'].iloc[-1])
            volatility = float(min(atr / current_price * 10, 1.0))  # normalize
        else:
            volatility = 0.5  # default
        
        # ========================================
        # 4️⃣ Momentum
        # ========================================
        # Momentum = (prob_up - prob_down) * trend_strength
        # محدوده: -1 (strong down) تا +1 (strong up)
        momentum = float((prob_up - prob_down) * trend_strength)
        
        # Metadata
        metadata = {
            'model': self.model.name,
            'current_price': float(market_data.data[-1].close),
            'timestamp': market_data.data[-1].datetime.isoformat(),
            'features_used': list(current_features.columns),
            'raw_prediction': int(1 if prob_up > prob_down else 0)  # برای reference
        }
        
        return MLAgentOutput(
            prob_up=prob_up,
            prob_down=prob_down,
            trend_strength=trend_strength,
            volatility=volatility,
            momentum=momentum,
            metadata=metadata
        )
    
    def load_model(self, path: Optional[str] = None):
        """بارگذاری model از فایل"""
        model_path = path or self.model_path
        
        if not Path(model_path).exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        print(f"Loading model from {model_path}...")
        self.model.load(model_path)
        
        # بعد از load، مطمئن شو که is_trained = True است
        if not self.model.is_trained:
            self.model.is_trained = True
        
        print(f"Model loaded successfully!")
    
    def get_feature_importance(self, top_n: int = 20) -> Dict[str, float]:
        """
        دریافت مهم‌ترین features
        
        Args:
            top_n: تعداد top features
        
        Returns:
            Dict of {feature_name: importance_score}
        """
        if not self.model.is_trained:
            return {}
        
        importance = self.model.get_feature_importance()
        sorted_importance = sorted(importance.items(), key=lambda x: x[1], reverse=True)
        
        return dict(sorted_importance[:top_n])
    
    def explain_prediction(self, market_data: MarketData) -> Dict[str, Any]:
        """
        توضیح دلیل prediction
        
        Returns:
            Dict با اطلاعات تفصیلی
        """
        output = self.analyze(market_data)
        
        # Top features و مقادیرشان
        importance = self.get_feature_importance(top_n=10)
        
        if self.last_features is not None:
            feature_values = {}
            for feature in importance.keys():
                if feature in self.last_features.columns:
                    feature_values[feature] = float(self.last_features[feature].iloc[0])
        else:
            feature_values = {}
        
        return {
            'recommendation': output.recommendation,
            'confidence': output.confidence,
            'reason': output.reason,
            'prediction': output.metadata['prediction'],
            'probabilities': {
                'up': output.metadata['probability_up'],
                'down': output.metadata['probability_down']
            },
            'top_features': {
                'importance': importance,
                'current_values': feature_values
            },
            'model': self.model.name
        }
    
    def backtest_predictions(
        self,
        market_data: MarketData,
        window_size: int = 100
    ) -> Dict[str, Any]:
        """
        Backtest predictions روی historical data
        
        Args:
            market_data: داده تاریخی
            window_size: اندازه پنجره برای هر prediction
        
        Returns:
            Backtest results با accuracy و metrics
        """
        print(f"\n{'='*60}")
        print(f"Backtesting ML Predictions")
        print(f"{'='*60}")
        
        predictions = []
        actuals = []
        confidences = []
        
        # استخراج features یک بار
        df = self.feature_engineer.extract_features(market_data)
        feature_cols = [col for col in df.columns if col not in ['target', 'target_return', 'future_close']]
        
        # Simulate rolling predictions
        for i in range(window_size, len(df)):
            X = df[feature_cols].iloc[[i]]
            y_true = df['target'].iloc[i]
            
            pred = self.model.predict(X)[0]
            proba = self.model.predict_proba(X)[0]
            conf = proba[1] if pred == 1 else proba[0]
            
            predictions.append(pred)
            actuals.append(y_true)
            confidences.append(conf)
        
        predictions = np.array(predictions)
        actuals = np.array(actuals)
        confidences = np.array(confidences)
        
        # محاسبه metrics
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
        
        accuracy = accuracy_score(actuals, predictions)
        precision = precision_score(actuals, predictions, zero_division=0)
        recall = recall_score(actuals, predictions, zero_division=0)
        f1 = f1_score(actuals, predictions, zero_division=0)
        cm = confusion_matrix(actuals, predictions)
        
        # Trades based on confidence threshold
        high_conf_mask = confidences >= self.confidence_threshold
        if high_conf_mask.sum() > 0:
            high_conf_accuracy = accuracy_score(
                actuals[high_conf_mask],
                predictions[high_conf_mask]
            )
        else:
            high_conf_accuracy = 0
        
        results = {
            'total_predictions': len(predictions),
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'confusion_matrix': cm.tolist(),
            'high_confidence_trades': int(high_conf_mask.sum()),
            'high_confidence_accuracy': high_conf_accuracy,
            'avg_confidence': float(np.mean(confidences))
        }
        
        # نمایش
        print(f"\nBacktest Results:")
        print(f"  Total Predictions: {results['total_predictions']}")
        print(f"  Accuracy: {results['accuracy']:.2%}")
        print(f"  Precision: {results['precision']:.2%}")
        print(f"  Recall: {results['recall']:.2%}")
        print(f"  F1 Score: {results['f1_score']:.2%}")
        print(f"\nHigh Confidence Trades (>={self.confidence_threshold:.0%}):")
        print(f"  Count: {results['high_confidence_trades']}")
        print(f"  Accuracy: {results['high_confidence_accuracy']:.2%}")
        print(f"\nConfusion Matrix:")
        print(f"  [[TN={cm[0,0]}, FP={cm[0,1]}]")
        print(f"   [FN={cm[1,0]}, TP={cm[1,1]}]]")
        print(f"{'='*60}\n")
        
        return results
