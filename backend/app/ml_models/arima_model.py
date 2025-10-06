import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
import warnings
warnings.filterwarnings('ignore')

class ARIMAForecaster:
    """ARIMA model for time series forecasting"""
    
    def __init__(self, order=(5, 1, 2)):
        self.order = order
        self.model = None
        self.fitted_model = None
        
    def fit(self, data):
        """
        Fit ARIMA model to historical data
        
        Args:
            data: pandas Series or numpy array of closing prices
        """
        # Convert to pandas Series if numpy array
        if isinstance(data, np.ndarray):
            data = pd.Series(data)
        
        # Check stationarity
        try:
            adf_result = adfuller(data.dropna())
            # p-value > 0.05 means non-stationary
            d = 1 if adf_result[1] > 0.05 else 0
        except:
            d = 1  # Default to differencing if test fails
            
        order = (self.order[0], d, self.order[2])
        
        try:
            self.model = ARIMA(data, order=order)
            self.fitted_model = self.model.fit()
        except Exception as e:
            # Fallback to simpler model if fitting fails
            print(f"ARIMA fit failed with order {order}, trying simpler model: {e}")
            order = (1, 1, 1)
            self.model = ARIMA(data, order=order)
            self.fitted_model = self.model.fit()
        
        return self
    
    def predict(self, steps):
        """
        Generate forecasts
        
        Args:
            steps: Number of time steps to forecast
            
        Returns:
            predictions: Array of predicted values
            conf_int: Confidence intervals (lower, upper) as numpy array
        """
        if self.fitted_model is None:
            raise ValueError("Model must be fitted before prediction")
        
        # Get forecast
        forecast_result = self.fitted_model.forecast(steps=steps)
        
        # Convert to numpy array if not already
        if isinstance(forecast_result, pd.Series):
            predictions = forecast_result.values
        else:
            predictions = np.array(forecast_result)
        
        # Get confidence intervals
        forecast_obj = self.fitted_model.get_forecast(steps=steps)
        conf_int = forecast_obj.conf_int()
        
        # Convert confidence intervals to numpy array
        if isinstance(conf_int, pd.DataFrame):
            conf_int_array = conf_int.values
        else:
            conf_int_array = np.array(conf_int)
        
        return predictions, conf_int_array
    
    def get_params(self):
        """Get model parameters"""
        if self.fitted_model is None:
            return {
                'order': self.order,
                'aic': None,
                'bic': None
            }
        
        return {
            'order': self.order,
            'aic': float(self.fitted_model.aic),
            'bic': float(self.fitted_model.bic)
        }