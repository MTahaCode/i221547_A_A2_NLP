import numpy as np
from app.ml_models.arima_model import ARIMAForecaster
from app.ml_models.lstm_model import LSTMForecaster
from app.ml_models.gru_model import GRUForecaster
from app.ml_models.transformer_model import TransformerForecaster

class EnsembleForecaster:
    """Ensemble model combining multiple forecasters"""
    
    def __init__(self, weights=None):
        """
        Initialize ensemble
        
        Args:
            weights: Dict of model weights (e.g., {'arima': 0.3, 'lstm': 0.3, 'gru': 0.2, 'transformer': 0.2})
        """
        self.models = {
            'arima': ARIMAForecaster(),
            'lstm': LSTMForecaster(epochs=30),
            'gru': GRUForecaster(epochs=30),
            'transformer': TransformerForecaster(epochs=30)
        }
        
        # Default equal weights if not specified
        if weights is None:
            n_models = len(self.models)
            self.weights = {name: 1.0/n_models for name in self.models.keys()}
        else:
            self.weights = weights
            
        self.fitted_models = {}
        
    def fit(self, data):
        """
        Train all models in the ensemble
        
        Args:
            data: numpy array of closing prices
        """
        print("Training ensemble models...")
        
        for name, model in self.models.items():
            print(f"\nTraining {name.upper()}...")
            try:
                model.fit(data)
                self.fitted_models[name] = model
                print(f"{name.upper()} training complete")
            except Exception as e:
                print(f"Error training {name}: {str(e)}")
                
        return self
    
    def predict(self, data, steps):
        """
        Generate ensemble forecast
        
        Args:
            data: Recent historical data
            steps: Number of time steps to forecast
            
        Returns:
            predictions: Weighted average of all model predictions
            individual_predictions: Dict of predictions from each model
        """
        individual_predictions = {}
        
        for name, model in self.fitted_models.items():
            try:
                if name == 'arima':
                    preds, _ = model.predict(steps)
                else:
                    preds = model.predict(data, steps)
                individual_predictions[name] = preds
            except Exception as e:
                print(f"Error in {name} prediction: {str(e)}")
        
        if not individual_predictions:
            raise ValueError("No models successfully generated predictions")
        
        # Calculate weighted average
        ensemble_pred = np.zeros(steps)
        total_weight = 0
        
        for name, preds in individual_predictions.items():
            weight = self.weights.get(name, 0)
            ensemble_pred += weight * preds
            total_weight += weight
        
        # Normalize by total weight
        if total_weight > 0:
            ensemble_pred /= total_weight
        
        return ensemble_pred, individual_predictions
    
    def update_weights(self, performance_metrics):
        """
        Update model weights based on recent performance
        
        Args:
            performance_metrics: Dict of {model_name: rmse_score}
        """
        # Inverse of RMSE as weights (lower RMSE = higher weight)
        inverse_errors = {name: 1.0/max(rmse, 0.001) 
                         for name, rmse in performance_metrics.items()}
        
        total = sum(inverse_errors.values())
        self.weights = {name: val/total for name, val in inverse_errors.items()}
        
        return self.weights
    
    def get_params(self):
        """Get ensemble parameters"""
        return {
            'weights': self.weights,
            'models': list(self.fitted_models.keys())
        }