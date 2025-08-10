import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the trading bot"""
    
    # API Configuration
    API_KEY = os.getenv('BINANCE_API_KEY')
    API_SECRET = os.getenv('BINANCE_SECRET_KEY')
    
    # Binance URLs
    TESTNET_BASE_URL = 'https://testnet.binancefuture.com'
    TESTNET_WS_URL = 'wss://stream.binancefuture.com'
    
    # Default Trading Parameters
    DEFAULT_SYMBOL = os.getenv('DEFAULT_SYMBOL', 'BTCUSDT')
    DEFAULT_QUANTITY = float(os.getenv('DEFAULT_QUANTITY', '0.01'))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Order Types
    ORDER_TYPES = {
        'MARKET': 'MARKET',
        'LIMIT': 'LIMIT',
        'STOP_MARKET': 'STOP_MARKET',
        'STOP_LIMIT': 'STOP',  # For OCO orders
        'TAKE_PROFIT': 'TAKE_PROFIT',
        'TAKE_PROFIT_MARKET': 'TAKE_PROFIT_MARKET'
    }
    
    # Order Sides
    ORDER_SIDES = {
        'BUY': 'BUY',
        'SELL': 'SELL'
    }
    
    # Time in Force
    TIME_IN_FORCE = {
        'GTC': 'GTC',  # Good Till Cancel
        'IOC': 'IOC',  # Immediate or Cancel
        'FOK': 'FOK'   # Fill or Kill
    }
    
    @classmethod
    def validate_config(cls):
        """Validate essential configuration"""
        if not cls.API_KEY or not cls.API_SECRET:
            raise ValueError("BINANCE_API_KEY and BINANCE_SECRET_KEY must be set in .env file")
        
        if cls.API_KEY == 'your_binance_testnet_api_key_here':
            raise ValueError("Please update BINANCE_API_KEY in .env file with your actual Binance testnet API key")
        
        if cls.API_SECRET == 'your_binance_testnet_api_secret_here':
            raise ValueError("Please update BINANCE_SECRET_KEY in .env file with your actual Binance testnet API secret")
        
        return True
