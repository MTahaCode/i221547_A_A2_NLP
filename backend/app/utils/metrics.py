import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def calculate_rmse(y_true, y_pred):
    """Calculate Root Mean Square Error"""
    return np.sqrt(mean_squared_error(y_true, y_pred))

def calculate_mae(y_true, y_pred):
    """Calculate Mean Absolute Error"""
    return mean_absolute_error(y_true, y_pred)

def calculate_mape(y_true, y_pred):
    """Calculate Mean Absolute Percentage Error"""
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    # Avoid division by zero
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100

def calculate_r2(y_true, y_pred):
    """Calculate R² Score"""
    return r2_score(y_true, y_pred)

def calculate_directional_accuracy(y_true, y_pred):
    """Calculate percentage of correct directional predictions"""
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    
    if len(y_true) < 2:
        return None
    
    true_direction = np.diff(y_true) > 0
    pred_direction = np.diff(y_pred) > 0
    
    return np.mean(true_direction == pred_direction) * 100

def calculate_all_metrics(y_true, y_pred):
    """Calculate all available metrics"""
    metrics = {}
    
    try:
        metrics['rmse'] = float(calculate_rmse(y_true, y_pred))
    except:
        pass
    
    try:
        metrics['mae'] = float(calculate_mae(y_true, y_pred))
    except:
        pass
    
    try:
        metrics['mape'] = float(calculate_mape(y_true, y_pred))
    except:
        pass
    
    try:
        metrics['r2_score'] = float(calculate_r2(y_true, y_pred))
    except:
        pass
    
    try:
        dir_acc = calculate_directional_accuracy(y_true, y_pred)
        if dir_acc is not None:
            metrics['directional_accuracy'] = float(dir_acc)
    except:
        pass
    
    return metrics