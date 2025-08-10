import logging
import os
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama for Windows
init(autoreset=True)

class Logger:
    def __init__(self, name="TradingBot", log_level=logging.INFO):
        """Initialize logger with file and console handlers"""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create logs directory
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # File handler
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"logs/trading_bot_{timestamp}.log"
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setLevel(log_level)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.info(f"Logger initialized. Logs saved to: {log_filename}")
    
    def debug(self, message):
        self.logger.debug(f"{Fore.CYAN}{message}{Style.RESET_ALL}")
    
    def info(self, message):
        self.logger.info(f"{Fore.GREEN}{message}{Style.RESET_ALL}")
    
    def warning(self, message):
        self.logger.warning(f"{Fore.YELLOW}{message}{Style.RESET_ALL}")
    
    def error(self, message):
        self.logger.error(f"{Fore.RED}{message}{Style.RESET_ALL}")
    
    def critical(self, message):
        self.logger.critical(f"{Fore.MAGENTA}{message}{Style.RESET_ALL}")
    
    def api_request(self, method, endpoint, params=None):
        """Log API requests"""
        params_str = f" | Params: {params}" if params else ""
        self.info(f"API Request: {method} {endpoint}{params_str}")
    
    def api_response(self, response_data, status_code=200):
        """Log API responses"""
        if status_code == 200:
            self.info(f"API Response: Success | Data: {str(response_data)[:200]}...")
        else:
            self.error(f"API Response: Error {status_code} | Data: {response_data}")
    
    def order_placed(self, order_details):
        """Log order placement"""
        self.info(f"ORDER PLACED: {order_details}")
    
    def order_failed(self, error_details):
        """Log order failures"""
        self.error(f"ORDER FAILED: {error_details}")
