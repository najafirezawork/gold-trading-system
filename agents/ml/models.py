"""
ML Models for price prediction
مدل‌های ML برای پیش‌بینی قیمت
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
from datetime import datetime
import pickle
import json
from pathlib import Path


class MLModel(ABC):
    """
    Base class برای ML models
    """
    
    def __init__(self, name: str):
        self.name = name
        self.model = None
        self.is_trained = False
        self.feature_importance: Optional[Dict[str, float]] = None
        self.training_metrics: Optional[Dict[str, float]] = None
    
    @abstractmethod
    def train(
        self, 
        X_train: pd.DataFrame, 
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None
    ) -> Dict[str, float]:
        """Train the model"""
        pass
    
    @abstractmethod
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict using the model"""
        pass
    
    @abstractmethod
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predict probabilities"""
        pass
    
    def save(self, path: str):
        """ذخیره model"""
        model_data = {
            'name': self.name,
            'model': self.model,
            'is_trained': self.is_trained,
            'feature_importance': self.feature_importance,
            'training_metrics': self.training_metrics
        }
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load(self, path: str):
        """بارگذاری model"""
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.name = model_data['name']
        self.model = model_data['model']
        self.is_trained = model_data['is_trained']
        self.feature_importance = model_data['feature_importance']
        self.training_metrics = model_data['training_metrics']
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Feature importance"""
        return self.feature_importance or {}


class RandomForestModel(MLModel):
    """
    Random Forest Classifier
    مناسب برای: پیش‌بینی جهت حرکت قیمت (UP/DOWN)
    """
    
    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: Optional[int] = 10,
        min_samples_split: int = 5,
        random_state: int = 42
    ):
        super().__init__("RandomForest")
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.random_state = random_state
    
    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None
    ) -> Dict[str, float]:
        """Train Random Forest"""
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        # ساخت model
        self.model = RandomForestClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            min_samples_split=self.min_samples_split,
            random_state=self.random_state,
            n_jobs=-1
        )
        
        # Train
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Feature importance
        self.feature_importance = dict(zip(
            X_train.columns,
            self.model.feature_importances_
        ))
        
        # Validation metrics
        metrics = {}
        
        if X_val is not None and y_val is not None:
            y_pred = self.predict(X_val)
            y_pred_proba = self.predict_proba(X_val)[:, 1]
            
            metrics['val_accuracy'] = accuracy_score(y_val, y_pred)
            metrics['val_precision'] = precision_score(y_val, y_pred, zero_division=0)
            metrics['val_recall'] = recall_score(y_val, y_pred, zero_division=0)
            metrics['val_f1'] = f1_score(y_val, y_pred, zero_division=0)
        
        # Training metrics
        y_train_pred = self.predict(X_train)
        metrics['train_accuracy'] = accuracy_score(y_train, y_train_pred)
        
        self.training_metrics = metrics
        
        return metrics
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict class (0 or 1)"""
        if not self.is_trained:
            raise ValueError("Model not trained yet!")
        return self.model.predict(X)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predict probabilities [P(class=0), P(class=1)]"""
        if not self.is_trained:
            raise ValueError("Model not trained yet!")
        return self.model.predict_proba(X)


class XGBoostModel(MLModel):
    """
    XGBoost Classifier
    معمولاً accuracy بهتری نسبت به Random Forest دارد
    """
    
    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 6,
        learning_rate: float = 0.1,
        random_state: int = 42
    ):
        super().__init__("XGBoost")
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.random_state = random_state
    
    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None
    ) -> Dict[str, float]:
        """Train XGBoost"""
        try:
            import xgboost as xgb
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        except ImportError:
            raise ImportError("xgboost not installed. Run: pip install xgboost")
        
        # ساخت model
        self.model = xgb.XGBClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            learning_rate=self.learning_rate,
            random_state=self.random_state,
            use_label_encoder=False,
            eval_metric='logloss'
        )
        
        # Train با early stopping
        eval_set = [(X_train, y_train)]
        if X_val is not None and y_val is not None:
            eval_set.append((X_val, y_val))
        
        self.model.fit(
            X_train, y_train,
            eval_set=eval_set,
            verbose=False
        )
        
        self.is_trained = True
        
        # Feature importance
        self.feature_importance = dict(zip(
            X_train.columns,
            self.model.feature_importances_
        ))
        
        # Metrics
        metrics = {}
        
        if X_val is not None and y_val is not None:
            y_pred = self.predict(X_val)
            
            metrics['val_accuracy'] = accuracy_score(y_val, y_pred)
            metrics['val_precision'] = precision_score(y_val, y_pred, zero_division=0)
            metrics['val_recall'] = recall_score(y_val, y_pred, zero_division=0)
            metrics['val_f1'] = f1_score(y_val, y_pred, zero_division=0)
        
        y_train_pred = self.predict(X_train)
        metrics['train_accuracy'] = accuracy_score(y_train, y_train_pred)
        
        self.training_metrics = metrics
        
        return metrics
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict class"""
        if not self.is_trained:
            raise ValueError("Model not trained yet!")
        return self.model.predict(X)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predict probabilities"""
        if not self.is_trained:
            raise ValueError("Model not trained yet!")
        return self.model.predict_proba(X)


class EnsembleModel(MLModel):
    """
    Ensemble از چند model
    Voting یا averaging برای پیش‌بینی نهایی
    """
    
    def __init__(self, models: list[MLModel] = None, voting: str = 'soft'):
        """
        Args:
            models: لیست models (اختیاری برای load)
            voting: 'soft' (average probabilities) یا 'hard' (majority vote)
        """
        super().__init__("Ensemble")
        self.models = models or []
        self.voting = voting
    
    def save(self, path: str):
        """ذخیره ensemble و همه models داخلی"""
        model_data = {
            'name': self.name,
            'models': self.models,
            'voting': self.voting,
            'is_trained': self.is_trained,
            'feature_importance': self.feature_importance,
            'training_metrics': self.training_metrics
        }
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load(self, path: str):
        """بارگذاری ensemble"""
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.name = model_data['name']
        self.models = model_data['models']
        self.voting = model_data.get('voting', 'soft')
        self.is_trained = model_data['is_trained']
        self.feature_importance = model_data.get('feature_importance')
        self.training_metrics = model_data.get('training_metrics')
    
    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None
    ) -> Dict[str, float]:
        """Train all models"""
        from sklearn.metrics import accuracy_score
        
        all_metrics = {}
        
        for i, model in enumerate(self.models):
            print(f"Training {model.name}...")
            metrics = model.train(X_train, y_train, X_val, y_val)
            all_metrics[f"{model.name}_{i}"] = metrics
        
        self.is_trained = True
        
        # Overall metrics
        if X_val is not None and y_val is not None:
            y_pred = self.predict(X_val)
            overall_accuracy = accuracy_score(y_val, y_pred)
            all_metrics['ensemble_val_accuracy'] = overall_accuracy
        
        self.training_metrics = all_metrics
        
        return all_metrics
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict using voting"""
        if not self.is_trained:
            raise ValueError("Models not trained yet!")
        
        if self.voting == 'soft':
            # Average probabilities
            all_proba = np.array([model.predict_proba(X)[:, 1] for model in self.models])
            avg_proba = np.mean(all_proba, axis=0)
            return (avg_proba >= 0.5).astype(int)
        else:
            # Hard voting (majority)
            all_preds = np.array([model.predict(X) for model in self.models])
            return (np.mean(all_preds, axis=0) >= 0.5).astype(int)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Average probabilities from all models"""
        if not self.is_trained:
            raise ValueError("Models not trained yet!")
        
        all_proba = np.array([model.predict_proba(X) for model in self.models])
        avg_proba = np.mean(all_proba, axis=0)
        return avg_proba
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Average feature importance across models"""
        if not self.models:
            return {}
        
        all_importance = {}
        
        for model in self.models:
            importance = model.get_feature_importance()
            for feature, value in importance.items():
                if feature not in all_importance:
                    all_importance[feature] = []
                all_importance[feature].append(value)
        
        # Average
        return {
            feature: np.mean(values)
            for feature, values in all_importance.items()
        }
