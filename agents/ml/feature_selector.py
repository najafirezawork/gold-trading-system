"""
Advanced Feature Selection for ML models
انتخاب بهترین features به صورت اتوماتیک برای جلوگیری از overfitting
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.feature_selection import (
    SelectKBest, f_classif, chi2, mutual_info_classif,
    RFE, RFECV, VarianceThreshold
)
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LassoCV
from sklearn.model_selection import cross_val_score, TimeSeriesSplit
import warnings
warnings.filterwarnings('ignore')


class AdvancedFeatureSelector:
    """
    انتخاب بهترین features به صورت اتوماتیک
    
    روش‌های انتخاب:
    1. حذف features با variance پایین
    2. حذف features با همبستگی بالا
    3. انتخاب آماری (f_classif, mutual_info)
    4. انتخاب مبتنی بر model (RFE با RandomForest)
    5. انتخاب مبتنی بر Lasso regularization
    """
    
    def __init__(
        self,
        n_features: int = 30,
        correlation_threshold: float = 0.95,
        variance_threshold: float = 0.01,
        cv_folds: int = 3
    ):
        """
        Args:
            n_features: تعداد نهایی features مورد نظر
            correlation_threshold: حد آستانه برای حذف features همبسته
            variance_threshold: حد آستانه برای حذف features با variance پایین
            cv_folds: تعداد folds برای cross-validation
        """
        self.n_features = n_features
        self.correlation_threshold = correlation_threshold
        self.variance_threshold = variance_threshold
        self.cv_folds = cv_folds
        
        # Selected features tracker
        self.selected_features: Optional[List[str]] = None
        self.feature_scores: Optional[Dict[str, float]] = None
        self.selection_history: Dict[str, List[str]] = {}
        
    def select_features(
        self, 
        X: pd.DataFrame, 
        y: pd.Series,
        method: str = 'combined'
    ) -> pd.DataFrame:
        """
        انتخاب بهترین features
        
        Args:
            X: DataFrame با features
            y: target variable
            method: روش انتخاب ('statistical', 'model_based', 'lasso', 'combined')
            
        Returns:
            DataFrame با features انتخاب شده
        """
        print(f"🔍 شروع Feature Selection با {len(X.columns)} features...")
        
        # 1. Data cleaning
        X_clean = self._clean_features(X, y)
        print(f"✅ بعد از cleaning: {len(X_clean.columns)} features")
        
        # 2. Remove low variance features
        X_variance = self._remove_low_variance_features(X_clean)
        print(f"✅ بعد از حذف low variance: {len(X_variance.columns)} features")
        self.selection_history['after_variance'] = list(X_variance.columns)
        
        # 3. Remove highly correlated features
        X_corr = self._remove_correlated_features(X_variance)
        print(f"✅ بعد از حذف correlated: {len(X_corr.columns)} features")
        self.selection_history['after_correlation'] = list(X_corr.columns)
        
        # 4. Feature selection based on method
        if method == 'statistical':
            X_selected = self._statistical_selection(X_corr, y)
        elif method == 'model_based':
            X_selected = self._model_based_selection(X_corr, y)
        elif method == 'lasso':
            X_selected = self._lasso_selection(X_corr, y)
        elif method == 'combined':
            X_selected = self._combined_selection(X_corr, y)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        print(f"✅ Features نهایی: {len(X_selected.columns)}")
        self.selected_features = list(X_selected.columns)
        self.selection_history['final'] = self.selected_features
        
        return X_selected
    
    def _clean_features(self, X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
        """پاک‌سازی اولیه features"""
        # Remove features with too many NaN values
        X_clean = X.copy()
        
        # Remove columns with >50% NaN
        nan_threshold = len(X_clean) * 0.5
        X_clean = X_clean.dropna(thresh=nan_threshold, axis=1)
        
        # Remove infinite values
        X_clean = X_clean.replace([np.inf, -np.inf], np.nan)
        
        # Fill remaining NaN with median
        X_clean = X_clean.fillna(X_clean.median())
        
        # Remove features that are constant
        nunique = X_clean.nunique()
        constant_features = nunique[nunique == 1].index
        X_clean = X_clean.drop(columns=constant_features)
        
        return X_clean
    
    def _remove_low_variance_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """حذف features با variance پایین"""
        selector = VarianceThreshold(threshold=self.variance_threshold)
        
        try:
            X_selected = selector.fit_transform(X)
            selected_columns = X.columns[selector.get_support()]
            return pd.DataFrame(X_selected, columns=selected_columns, index=X.index)
        except Exception:
            # اگر خطا بود، همه features را نگه دار
            return X
    
    def _remove_correlated_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """حذف features با همبستگی بالا"""
        corr_matrix = X.corr().abs()
        
        # Find upper triangle of correlation matrix
        upper_tri = corr_matrix.where(
            np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
        )
        
        # Find features with correlation greater than threshold
        to_drop = [
            column for column in upper_tri.columns 
            if any(upper_tri[column] > self.correlation_threshold)
        ]
        
        return X.drop(columns=to_drop)
    
    def _statistical_selection(self, X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
        """انتخاب مبتنی بر آمار"""
        # انتخاب بر اساس f_classif
        selector_f = SelectKBest(
            score_func=f_classif, 
            k=min(self.n_features, len(X.columns))
        )
        
        try:
            X_selected = selector_f.fit_transform(X, y)
            selected_features = X.columns[selector_f.get_support()]
            
            # Store scores
            scores = selector_f.scores_
            self.feature_scores = dict(zip(selected_features, scores[selector_f.get_support()]))
            
            return pd.DataFrame(X_selected, columns=selected_features, index=X.index)
        except Exception:
            # اگر خطا بود، اولین n_features را برگردان
            return X.iloc[:, :self.n_features]
    
    def _model_based_selection(self, X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
        """انتخاب مبتنی بر RandomForest"""
        rf = RandomForestClassifier(
            n_estimators=50, 
            random_state=42,
            n_jobs=-1,
            max_depth=5  # جلوگیری از overfitting
        )
        
        try:
            # استفاده از TimeSeriesSplit برای cross-validation
            cv = TimeSeriesSplit(n_splits=self.cv_folds)
            
            selector = RFECV(
                estimator=rf,
                step=1,
                cv=cv,
                scoring='accuracy',
                n_jobs=-1,
                min_features_to_select=min(10, self.n_features)
            )
            
            X_selected = selector.fit_transform(X, y)
            selected_features = X.columns[selector.get_support()]
            
            # اگر بیش از حد نظر features انتخاب شد، کاهش بده
            if len(selected_features) > self.n_features:
                # بر اساس feature importance انتخاب کن
                rf.fit(X[selected_features], y)
                importances = rf.feature_importances_
                
                # Sort by importance and select top n_features
                feature_importance = list(zip(selected_features, importances))
                feature_importance.sort(key=lambda x: x[1], reverse=True)
                
                final_features = [f[0] for f in feature_importance[:self.n_features]]
                selected_features = final_features
                X_selected = X[selected_features]
            
            self.feature_scores = dict(zip(
                selected_features, 
                [selector.estimator_.feature_importances_[i] for i in range(len(selected_features))]
            ))
            
            return pd.DataFrame(X_selected, columns=selected_features, index=X.index)
            
        except Exception as e:
            print(f"⚠️ خطا در model-based selection: {e}")
            # fallback to statistical method
            return self._statistical_selection(X, y)
    
    def _lasso_selection(self, X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
        """انتخاب مبتنی بر Lasso regularization"""
        try:
            # استفاده از LassoCV برای انتخاب بهترین alpha
            lasso = LassoCV(
                cv=TimeSeriesSplit(n_splits=self.cv_folds),
                random_state=42,
                max_iter=1000
            )
            
            lasso.fit(X, y)
            
            # Features with non-zero coefficients
            selected_mask = lasso.coef_ != 0
            selected_features = X.columns[selected_mask]
            
            # اگر خیلی کم features انتخاب شد، از statistical fallback استفاده کن
            if len(selected_features) < 5:
                return self._statistical_selection(X, y)
            
            # اگر خیلی زیاد انتخاب شد، top n_features را بر اساس abs(coefficient) انتخاب کن
            if len(selected_features) > self.n_features:
                coef_abs = np.abs(lasso.coef_[selected_mask])
                feature_coef = list(zip(selected_features, coef_abs))
                feature_coef.sort(key=lambda x: x[1], reverse=True)
                
                final_features = [f[0] for f in feature_coef[:self.n_features]]
                selected_features = final_features
            
            self.feature_scores = dict(zip(
                selected_features,
                np.abs(lasso.coef_[X.columns.isin(selected_features)])
            ))
            
            return X[selected_features]
            
        except Exception as e:
            print(f"⚠️ خطا در lasso selection: {e}")
            return self._statistical_selection(X, y)
    
    def _combined_selection(self, X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
        """ترکیب چند روش برای انتخاب بهترین features"""
        
        # 1. Statistical selection (50% of target features)
        n_statistical = max(self.n_features // 2, 10)
        try:
            X_stat = self._statistical_selection(X, y)
            if len(X_stat.columns) > n_statistical:
                X_stat = X_stat.iloc[:, :n_statistical]
            stat_features = set(X_stat.columns)
        except Exception:
            stat_features = set()
        
        # 2. Model-based selection
        try:
            X_model = self._model_based_selection(X, y)
            model_features = set(X_model.columns)
        except Exception:
            model_features = set()
        
        # 3. Lasso selection
        try:
            X_lasso = self._lasso_selection(X, y)
            lasso_features = set(X_lasso.columns)
        except Exception:
            lasso_features = set()
        
        # Combine: features that appear in at least 2 methods
        all_methods = [stat_features, model_features, lasso_features]
        vote_count = {}
        
        for features in all_methods:
            for feature in features:
                vote_count[feature] = vote_count.get(feature, 0) + 1
        
        # Select features with at least 2 votes, or top voted ones
        high_voted = [f for f, votes in vote_count.items() if votes >= 2]
        
        if len(high_voted) < self.n_features:
            # اضافه کردن features با بیشترین vote
            sorted_features = sorted(vote_count.items(), key=lambda x: x[1], reverse=True)
            for feature, _ in sorted_features:
                if feature not in high_voted and len(high_voted) < self.n_features:
                    high_voted.append(feature)
        
        # محدود کردن به n_features
        if len(high_voted) > self.n_features:
            high_voted = high_voted[:self.n_features]
        
        # اطمینان از اینکه features موجود هستند
        final_features = [f for f in high_voted if f in X.columns]
        
        if len(final_features) == 0:
            # fallback: اولین n_features
            final_features = list(X.columns[:self.n_features])
        
        self.feature_scores = {f: vote_count.get(f, 0) for f in final_features}
        
        return X[final_features]
    
    def get_selection_report(self) -> Dict:
        """گزارش کامل از فرآیند انتخاب features"""
        if not self.selected_features:
            return {"error": "هنوز feature selection انجام نشده است"}
        
        return {
            "selected_features_count": len(self.selected_features),
            "selected_features": self.selected_features,
            "feature_scores": self.feature_scores,
            "selection_history": self.selection_history,
            "top_features": sorted(
                self.feature_scores.items() if self.feature_scores else [],
                key=lambda x: x[1], 
                reverse=True
            )[:10] if self.feature_scores else []
        }
    
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """اعمال feature selection به داده جدید"""
        if not self.selected_features:
            raise ValueError("ابتدا باید select_features() را صدا بزنید")
        
        # انتخاب فقط features که در training انتخاب شده‌اند
        available_features = [f for f in self.selected_features if f in X.columns]
        
        if len(available_features) == 0:
            raise ValueError("هیچ‌کدام از features انتخاب شده در داده جدید موجود نیست")
        
        return X[available_features]