"""
GDP Prediction Model using Linear Regression
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error
from typing import Tuple, Dict


class GDPPredictor:
    """Machine learning model for GDP prediction"""
    
    def __init__(self):
        self.models = {}  # Store one model per country
        self.metrics = {}  # Store model performance metrics
    
    def train(self, df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """
        Train linear regression models for each country
        
        Args:
            df: DataFrame with columns: country, year, value
            
        Returns:
            Dictionary of model metrics for each country
        """
        self.models = {}
        self.metrics = {}
        
        for country in df['country'].unique():
            country_data = df[df['country'] == country].sort_values('year')
            
            if len(country_data) < 3:  # Need at least 3 points for training
                continue
            
            X = country_data['year'].values.reshape(-1, 1)
            y = country_data['value'].values
            
            # Train model
            model = LinearRegression()
            model.fit(X, y)
            
            # Calculate metrics
            y_pred = model.predict(X)
            r2 = r2_score(y, y_pred)
            mae = mean_absolute_error(y, y_pred)
            
            self.models[country] = model
            self.metrics[country] = {
                'r2_score': r2,
                'mae': mae,
                'coefficient': model.coef_[0],
                'intercept': model.intercept_
            }
        
        return self.metrics
    
    def predict(self, country: str, years: list) -> pd.DataFrame:
        """
        Predict GDP for specific years
        
        Args:
            country: Country name
            years: List of years to predict
            
        Returns:
            DataFrame with columns: country, year, value
        """
        if country not in self.models:
            raise ValueError(f"No model trained for {country}")
        
        model = self.models[country]
        X = np.array(years).reshape(-1, 1)
        predictions = model.predict(X)
        
        return pd.DataFrame({
            'country': [country] * len(years),
            'year': years,
            'value': predictions
        })
    
    def predict_next_year(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Predict GDP for the next year for all countries
        
        Args:
            df: DataFrame with historical data
            
        Returns:
            DataFrame with predictions for next year
        """
        # Train models if not already trained
        if not self.models:
            self.train(df)
        
        predictions = []
        
        for country in df['country'].unique():
            if country not in self.models:
                continue
            
            country_data = df[df['country'] == country]
            last_year = country_data['year'].max()
            next_year = last_year + 1
            
            pred = self.predict(country, [next_year])
            predictions.append(pred)
        
        if not predictions:
            return pd.DataFrame(columns=['country', 'year', 'value'])
        
        return pd.concat(predictions, ignore_index=True)
    
    def get_model_summary(self, country: str) -> str:
        """
        Get a human-readable summary of the model
        
        Args:
            country: Country name
            
        Returns:
            String description of the model
        """
        if country not in self.metrics:
            return f"No model available for {country}"
        
        metrics = self.metrics[country]
        coef = metrics['coefficient']
        intercept = metrics['intercept']
        r2 = metrics['r2_score']
        mae = metrics['mae']
        
        # Format coefficient
        if abs(coef) >= 1e9:
            coef_str = f"${coef/1e9:.2f}B"
        elif abs(coef) >= 1e6:
            coef_str = f"${coef/1e6:.2f}M"
        else:
            coef_str = f"${coef:,.0f}"
        
        # Format MAE
        if abs(mae) >= 1e12:
            mae_str = f"${mae/1e12:.2f}T"
        elif abs(mae) >= 1e9:
            mae_str = f"${mae/1e9:.2f}B"
        elif abs(mae) >= 1e6:
            mae_str = f"${mae/1e6:.2f}M"
        else:
            mae_str = f"${mae:,.0f}"
        
        trend = "increasing" if coef > 0 else "decreasing"
        
        summary = f"""
**{country} GDP Prediction Model**

- **Trend**: GDP is {trend} by approximately {coef_str} per year
- **R² Score**: {r2:.4f} (model explains {r2*100:.1f}% of variance)
- **Mean Absolute Error**: {mae_str}
- **Model Equation**: GDP = {coef:.2e} × Year + {intercept:.2e}
        """.strip()
        
        return summary
    
    def predict_with_confidence(
        self,
        df: pd.DataFrame,
        years: list,
        confidence: float = 0.95
    ) -> pd.DataFrame:
        """
        Predict with confidence intervals (simplified approach)
        
        Args:
            df: Historical data
            years: Years to predict
            confidence: Confidence level (default 0.95)
            
        Returns:
            DataFrame with predictions and confidence bounds
        """
        if not self.models:
            self.train(df)
        
        all_predictions = []
        
        for country in df['country'].unique():
            if country not in self.models:
                continue
            
            # Get predictions
            pred = self.predict(country, years)
            
            # Calculate simple confidence bounds using MAE
            mae = self.metrics[country]['mae']
            margin = mae * 2  # Approximate 95% confidence
            
            pred['lower_bound'] = pred['value'] - margin
            pred['upper_bound'] = pred['value'] + margin
            
            all_predictions.append(pred)
        
        if not all_predictions:
            return pd.DataFrame()
        
        return pd.concat(all_predictions, ignore_index=True)


# Singleton instance
gdp_predictor = GDPPredictor()
