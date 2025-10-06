import torch
import torch.nn as nn
import numpy as np
from sklearn.preprocessing import MinMaxScaler

class LSTMModel(nn.Module):
    """LSTM Neural Network for time series forecasting"""
    
    def __init__(self, input_size=1, hidden_size=64, num_layers=2, dropout=0.2):
        super(LSTMModel, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout,
            batch_first=True
        )
        
        self.fc = nn.Linear(hidden_size, 1)
        
    def forward(self, x):
        # Initialize hidden state and cell state
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        # Forward propagate LSTM
        out, _ = self.lstm(x, (h0, c0))
        
        # Get last time step output
        out = self.fc(out[:, -1, :])
        
        return out

class LSTMForecaster:
    """Wrapper for LSTM model with training and prediction"""
    
    def __init__(self, sequence_length=60, hidden_size=64, num_layers=2, 
                 learning_rate=0.001, epochs=50):
        self.sequence_length = sequence_length
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.learning_rate = learning_rate
        self.epochs = epochs
        
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def prepare_data(self, data):
        """Prepare sequences for training"""
        # Scale data
        scaled_data = self.scaler.fit_transform(data.reshape(-1, 1))
        
        X, y = [], []
        for i in range(self.sequence_length, len(scaled_data)):
            X.append(scaled_data[i-self.sequence_length:i])
            y.append(scaled_data[i])
        
        return np.array(X), np.array(y)
    
    def fit(self, data):
        """
        Train LSTM model
        
        Args:
            data: numpy array of closing prices
        """
        X, y = self.prepare_data(data)
        
        # Convert to tensors
        X_tensor = torch.FloatTensor(X).to(self.device)
        y_tensor = torch.FloatTensor(y).to(self.device)
        
        # Initialize model
        self.model = LSTMModel(
            input_size=1,
            hidden_size=self.hidden_size,
            num_layers=self.num_layers
        ).to(self.device)
        
        # Loss and optimizer
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        
        # Training loop
        self.model.train()
        for epoch in range(self.epochs):
            optimizer.zero_grad()
            
            outputs = self.model(X_tensor)
            loss = criterion(outputs, y_tensor)
            
            loss.backward()
            optimizer.step()
            
            if (epoch + 1) % 10 == 0:
                print(f'Epoch [{epoch+1}/{self.epochs}], Loss: {loss.item():.4f}')
        
        return self
    
    def predict(self, data, steps):
        """
        Generate forecasts
        
        Args:
            data: Recent historical data for context
            steps: Number of time steps to forecast
            
        Returns:
            predictions: Array of predicted values
        """
        if self.model is None:
            raise ValueError("Model must be fitted before prediction")
        
        self.model.eval()
        
        # Scale input data
        scaled_data = self.scaler.transform(data.reshape(-1, 1))
        
        # Use last sequence_length points as input
        current_sequence = scaled_data[-self.sequence_length:].reshape(1, self.sequence_length, 1)
        current_sequence = torch.FloatTensor(current_sequence).to(self.device)
        
        predictions = []
        
        with torch.no_grad():
            for _ in range(steps):
                # Predict next value
                pred = self.model(current_sequence)
                predictions.append(pred.cpu().numpy()[0, 0])
                
                # Update sequence with prediction
                pred_reshaped = pred.view(1, 1, 1)
                current_sequence = torch.cat((current_sequence[:, 1:, :], pred_reshaped), dim=1)
        
        # Inverse transform predictions
        predictions = np.array(predictions).reshape(-1, 1)
        predictions = self.scaler.inverse_transform(predictions)
        
        return predictions.flatten()
    
    def get_params(self):
        """Get model parameters"""
        return {
            'sequence_length': self.sequence_length,
            'hidden_size': self.hidden_size,
            'num_layers': self.num_layers,
            'learning_rate': self.learning_rate,
            'epochs': self.epochs
        }