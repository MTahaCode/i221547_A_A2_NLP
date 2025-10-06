def validate_symbol(symbol):
    """Validate instrument symbol"""
    if not symbol or not isinstance(symbol, str):
        raise ValueError("Symbol must be a non-empty string")
    return symbol.upper()

def validate_horizon(horizon, valid_horizons):
    """Validate forecast horizon"""
    if horizon not in valid_horizons:
        raise ValueError(f"Invalid horizon. Must be one of: {list(valid_horizons.keys())}")
    return horizon

def validate_model_type(model_type, available_models):
    """Validate model type"""
    if model_type not in available_models:
        raise ValueError(f"Invalid model type. Must be one of: {available_models}")
    return model_type