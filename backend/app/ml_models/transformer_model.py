import torch
import torch.nn as nn
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import math

class PositionalEncoding(nn.Module):
    """Positional encoding for transformer"""
    
    def __init__(self, d_model, max_len=5000):
        super(PositionalEncoding, self).__init__()
        
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)
        
    def forward(self, x):
        return x + self.pe[:, :x.size(1)]

class TransformerModel(nn.Module):
    """Transformer model for time series forecasting"""
    
    def __init__(self, input_size=1, d_model=64, nhead=4, num_layers=2, dropout=0.1):
        super(TransformerModel, self).__init__()
        
        self.input_projection = nn.Linear(input_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model)
        
        encoder_layers = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dropout=dropout,
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layers, num_layers)
        
        self.fc = nn.Linear(d_model, 1)
        
    def forward(self, x):
        x = self.input_projection(x)
        x = self.pos_encoder(x)
        x = self.transformer_encoder(x)
        x = self.fc(x[:, -1, :])
        return x

class TransformerForecaster:
    """Wrapper for Transformer model"""
    
    def __init__(self, sequence_length=60, d_model=64, nhead=4, num_layers=2,
                 learning_rate=0.001, epochs=50):
        self.sequence_length = sequence_length
        self.d_model = d_model
        self.nhead = nhead
        self.num_layers = num_layers
        self.learning_rate = learning_rate
        self.epochs = epochs
        
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def prepare_data(self, data):
        scaled_data = self.scaler.fit_transform(data.reshape(-1, 1))
        X, y = [], []
        for i in range(self.sequence_length, len(scaled_data)):
            X.append(scaled_data[i-self.sequence_length:i])
            y.append(scaled_data[i])
        return np.array(X), np.array(y)
    
    def fit(self, data):
        X, y = self.prepare_data(data)
        X_tensor = torch.FloatTensor(X).to(self.device)
        y_tensor = torch.FloatTensor(y).to(self.device)
        
        self.model = TransformerModel(
            input_size=1,
            d_model=self.d_model,
            nhead=self.nhead,
            num_layers=self.num_layers
        ).to(self.device)
        
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        
        self.model.train()
        for epoch in range(self.epochs):
            optimizer.zero_grad()
            outputs = self.model(X_tensor)
            loss = criterion(outputs, y_tensor)
            loss.backward()
            optimizer.step()
            
            if (epoch + 1) % 10 == 0:
                print(f'Transformer Epoch [{epoch+1}/{self.epochs}], Loss: {loss.item():.4f}')
        
        return self
    
    def predict(self, data, steps):
        if self.model is None:
            raise ValueError("Model must be fitted before prediction")
        
        self.model.eval()
        scaled_data = self.scaler.transform(data.reshape(-1, 1))
        current_sequence = scaled_data[-self.sequence_length:].reshape(1, self.sequence_length, 1)
        current_sequence = torch.FloatTensor(current_sequence).to(self.device)
        
        predictions = []
        with torch.no_grad():
            for _ in range(steps):
                pred = self.model(current_sequence)
                predictions.append(pred.cpu().numpy()[0, 0])
                pred_reshaped = pred.view(1, 1, 1)
                current_sequence = torch.cat((current_sequence[:, 1:, :], pred_reshaped), dim=1)
        
        predictions = np.array(predictions).reshape(-1, 1)
        predictions = self.scaler.inverse_transform(predictions)
        return predictions.flatten()
    
    def get_params(self):
        return {
            'sequence_length': self.sequence_length,
            'd_model': self.d_model,
            'nhead': self.nhead,
            'num_layers': self.num_layers,
            'learning_rate': self.learning_rate,
            'epochs': self.epochs
        }