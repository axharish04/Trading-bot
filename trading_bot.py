from binance import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
import time
import json
import requests
from typing import Dict, List, Optional, Union
from decimal import Decimal, ROUND_DOWN
from config import Config
from logger import Logger

class BasicBot:
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        """
        Initialize the trading bot
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            testnet: Whether to use testnet (default: True)
        """
        self.logger = Logger("TradingBot")
        
        try:
            # Initialize Binance client with timestamp offset
            self.client = Client(
                api_key=api_key,
                api_secret=api_secret,
                testnet=testnet
            )
            
            # Set testnet base URL
            if testnet:
                self.client.API_URL = Config.TESTNET_BASE_URL
            
            # Fix timestamp synchronization issue
            self._sync_time_offset()
            
            self.testnet = testnet
            
            # Test connectivity
            self._test_connectivity()
            
            # Get account info
            self.account_info = self._get_account_info()
            
            self.logger.info("Trading bot initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize trading bot: {str(e)}")
            raise
    
    def _sync_time_offset(self):
        """Synchronize time with Binance servers to fix timestamp issues"""
        try:
            # First, try to get server time via REST API directly
            self.logger.info("Synchronizing time with Binance servers...")
            
            url = "https://testnet.binancefuture.com/fapi/v1/time"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                server_time_data = response.json()
                server_timestamp = server_time_data['serverTime']
                
                # Get local time
                local_timestamp = int(time.time() * 1000)
                
                # Calculate offset with extra buffer for network latency
                time_offset = server_timestamp - local_timestamp + 1000  # Add 1 second buffer
                
                self.logger.info(f"Server time: {server_timestamp}")
                self.logger.info(f"Local time: {local_timestamp}")  
                self.logger.info(f"Time difference: {server_timestamp - local_timestamp}ms")
                self.logger.info(f"Applied offset (with buffer): {time_offset}ms")
                
                # Set timestamp offset for all future requests
                self.client.timestamp_offset = time_offset
                
                return time_offset
            else:
                raise Exception(f"Failed to get server time: HTTP {response.status_code}")
                
        except Exception as e:
            self.logger.warning(f"Could not sync time offset: {str(e)}")
            # Set a larger default offset to help with time sync issues
            default_offset = 5000  # 5 seconds
            self.client.timestamp_offset = default_offset
            self.logger.info(f"Using default time offset: {default_offset}ms")
            return default_offset
    
    def _test_connectivity(self):
        """Test API connectivity"""
        try:
            server_time = self.client.get_server_time()
            self.logger.info(f"Connected to Binance {'Testnet' if self.testnet else 'Mainnet'}")
            self.logger.debug(f"Server time: {server_time}")
            return True
        except Exception as e:
            self.logger.error(f"Connectivity test failed: {str(e)}")
            raise
    
    def _get_account_info(self):
        """Get account information"""
        try:
            account = self.client.futures_account()
            self.logger.api_request("GET", "/fapi/v2/account")
            self.logger.api_response(f"Balance: {account['totalWalletBalance']} USDT")
            return account
        except Exception as e:
            self.logger.error(f"Failed to get account info: {str(e)}")
            return None
    
    def get_balance(self) -> float:
        """Get USDT balance"""
        try:
            account = self.client.futures_account()
            for asset in account['assets']:
                if asset['asset'] == 'USDT':
                    balance = float(asset['walletBalance'])
                    self.logger.info(f"Current USDT balance: {balance}")
                    return balance
            return 0.0
        except Exception as e:
            self.logger.error(f"Failed to get balance: {str(e)}")
            return 0.0
    
    def get_symbol_info(self, symbol: str) -> Dict:
        """Get symbol information for proper quantity precision"""
        try:
            exchange_info = self.client.futures_exchange_info()
            for s in exchange_info['symbols']:
                if s['symbol'] == symbol:
                    return s
            raise ValueError(f"Symbol {symbol} not found")
        except Exception as e:
            self.logger.error(f"Failed to get symbol info for {symbol}: {str(e)}")
            raise
    
    def _format_quantity(self, symbol: str, quantity: float) -> str:
        """Format quantity according to symbol precision"""
        try:
            symbol_info = self.get_symbol_info(symbol)
            
            # Get quantity precision
            for f in symbol_info['filters']:
                if f['filterType'] == 'LOT_SIZE':
                    step_size = f['stepSize']
                    precision = len(step_size.rstrip('0').split('.')[-1]) if '.' in step_size else 0
                    
                    # Round down to avoid exceeding precision
                    multiplier = 10 ** precision
                    formatted_qty = int(quantity * multiplier) / multiplier
                    
                    return f"{formatted_qty:.{precision}f}"
            
            return str(quantity)
        except Exception as e:
            self.logger.error(f"Failed to format quantity: {str(e)}")
            return str(quantity)
    
    def _format_price(self, symbol: str, price: float) -> str:
        """Format price according to symbol precision"""
        try:
            symbol_info = self.get_symbol_info(symbol)
            
            # Get price precision
            for f in symbol_info['filters']:
                if f['filterType'] == 'PRICE_FILTER':
                    tick_size = f['tickSize']
                    precision = len(tick_size.rstrip('0').split('.')[-1]) if '.' in tick_size else 0
                    
                    # Round to nearest tick
                    tick_multiplier = 10 ** precision
                    formatted_price = round(price * tick_multiplier) / tick_multiplier
                    
                    return f"{formatted_price:.{precision}f}"
            
            return str(price)
        except Exception as e:
            self.logger.error(f"Failed to format price: {str(e)}")
            return str(price)
    
    def get_current_price(self, symbol: str) -> float:
        """Get current market price for a symbol"""
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])
            self.logger.debug(f"Current price for {symbol}: {price}")
            return price
        except Exception as e:
            self.logger.error(f"Failed to get current price for {symbol}: {str(e)}")
            raise
    
    def place_market_order(self, symbol: str, side: str, quantity: float) -> Dict:
        """
        Place a market order
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            side: Order side ('BUY' or 'SELL')
            quantity: Order quantity
            
        Returns:
            Order response dictionary
        """
        try:
            # Format quantity
            formatted_quantity = self._format_quantity(symbol, quantity)
            
            self.logger.api_request("POST", "/fapi/v1/order", {
                "symbol": symbol,
                "side": side,
                "type": "MARKET",
                "quantity": formatted_quantity
            })
            
            # Place the order
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=formatted_quantity
            )
            
            self.logger.order_placed({
                "orderId": order['orderId'],
                "symbol": symbol,
                "side": side,
                "type": "MARKET",
                "quantity": formatted_quantity,
                "status": order['status']
            })
            
            self.logger.api_response(order)
            return order
            
        except BinanceAPIException as e:
            error_msg = f"Binance API Error: {e.message} (Code: {e.code})"
            self.logger.order_failed(error_msg)
            raise
        except BinanceOrderException as e:
            error_msg = f"Order Error: {e.message} (Code: {e.code})"
            self.logger.order_failed(error_msg)
            raise
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.order_failed(error_msg)
            raise
    
    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float, 
                         time_in_force: str = 'GTC') -> Dict:
        """
        Place a limit order
        
        Args:
            symbol: Trading pair symbol
            side: Order side ('BUY' or 'SELL')
            quantity: Order quantity
            price: Limit price
            time_in_force: Time in force ('GTC', 'IOC', 'FOK')
            
        Returns:
            Order response dictionary
        """
        try:
            # Format quantity and price
            formatted_quantity = self._format_quantity(symbol, quantity)
            formatted_price = self._format_price(symbol, price)
            
            self.logger.api_request("POST", "/fapi/v1/order", {
                "symbol": symbol,
                "side": side,
                "type": "LIMIT",
                "quantity": formatted_quantity,
                "price": formatted_price,
                "timeInForce": time_in_force
            })
            
            # Place the order
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='LIMIT',
                quantity=formatted_quantity,
                price=formatted_price,
                timeInForce=time_in_force
            )
            
            self.logger.order_placed({
                "orderId": order['orderId'],
                "symbol": symbol,
                "side": side,
                "type": "LIMIT",
                "quantity": formatted_quantity,
                "price": formatted_price,
                "timeInForce": time_in_force,
                "status": order['status']
            })
            
            self.logger.api_response(order)
            return order
            
        except BinanceAPIException as e:
            error_msg = f"Binance API Error: {e.message} (Code: {e.code})"
            self.logger.order_failed(error_msg)
            raise
        except BinanceOrderException as e:
            error_msg = f"Order Error: {e.message} (Code: {e.code})"
            self.logger.order_failed(error_msg)
            raise
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.order_failed(error_msg)
            raise
    
    def place_stop_limit_order(self, symbol: str, side: str, quantity: float, 
                              stop_price: float, limit_price: float, 
                              time_in_force: str = 'GTC') -> Dict:
        """
        Place a stop-limit order
        
        Args:
            symbol: Trading pair symbol
            side: Order side ('BUY' or 'SELL')
            quantity: Order quantity
            stop_price: Stop price (trigger price)
            limit_price: Limit price (execution price)
            time_in_force: Time in force
            
        Returns:
            Order response dictionary
        """
        try:
            formatted_quantity = self._format_quantity(symbol, quantity)
            formatted_stop_price = self._format_price(symbol, stop_price)
            formatted_limit_price = self._format_price(symbol, limit_price)
            
            self.logger.api_request("POST", "/fapi/v1/order", {
                "symbol": symbol,
                "side": side,
                "type": "STOP",
                "quantity": formatted_quantity,
                "stopPrice": formatted_stop_price,
                "price": formatted_limit_price,
                "timeInForce": time_in_force
            })
            
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='STOP',
                quantity=formatted_quantity,
                stopPrice=formatted_stop_price,
                price=formatted_limit_price,
                timeInForce=time_in_force
            )
            
            self.logger.order_placed({
                "orderId": order['orderId'],
                "symbol": symbol,
                "side": side,
                "type": "STOP_LIMIT",
                "quantity": formatted_quantity,
                "stopPrice": formatted_stop_price,
                "price": formatted_limit_price,
                "status": order['status']
            })
            
            return order
            
        except Exception as e:
            error_msg = f"Stop-limit order failed: {str(e)}"
            self.logger.order_failed(error_msg)
            raise
    
    def place_oco_order(self, symbol: str, side: str, quantity: float, 
                       price: float, stop_price: float, stop_limit_price: float) -> Dict:
        """
        Place an OCO (One-Cancels-Other) order
        Note: This is a simplified OCO implementation using two separate orders
        """
        try:
            formatted_quantity = self._format_quantity(symbol, quantity)
            
            # Place limit order
            limit_order = self.place_limit_order(symbol, side, quantity, price)
            
            # Place stop-limit order
            opposite_side = 'SELL' if side == 'BUY' else 'BUY'
            stop_order = self.place_stop_limit_order(
                symbol, opposite_side, quantity, stop_price, stop_limit_price
            )
            
            oco_result = {
                "type": "OCO",
                "limitOrder": limit_order,
                "stopOrder": stop_order,
                "symbol": symbol,
                "quantity": formatted_quantity
            }
            
            self.logger.order_placed({
                "type": "OCO",
                "limitOrderId": limit_order['orderId'],
                "stopOrderId": stop_order['orderId'],
                "symbol": symbol,
                "quantity": formatted_quantity
            })
            
            return oco_result
            
        except Exception as e:
            error_msg = f"OCO order failed: {str(e)}"
            self.logger.order_failed(error_msg)
            raise
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict:
        """Cancel an order"""
        try:
            result = self.client.futures_cancel_order(symbol=symbol, orderId=order_id)
            self.logger.info(f"Order {order_id} cancelled successfully")
            return result
        except Exception as e:
            self.logger.error(f"Failed to cancel order {order_id}: {str(e)}")
            raise
    
    def get_order_status(self, symbol: str, order_id: int) -> Dict:
        """Get order status"""
        try:
            order = self.client.futures_get_order(symbol=symbol, orderId=order_id)
            self.logger.debug(f"Order {order_id} status: {order['status']}")
            return order
        except Exception as e:
            self.logger.error(f"Failed to get order status: {str(e)}")
            raise
    
    def get_open_orders(self, symbol: str = None) -> List[Dict]:
        """Get all open orders"""
        try:
            if symbol:
                orders = self.client.futures_get_open_orders(symbol=symbol)
            else:
                orders = self.client.futures_get_open_orders()
            
            self.logger.info(f"Found {len(orders)} open orders")
            return orders
        except Exception as e:
            self.logger.error(f"Failed to get open orders: {str(e)}")
            raise
    
    def get_order_history(self, symbol: str, limit: int = 10) -> List[Dict]:
        """Get order history"""
        try:
            orders = self.client.futures_get_all_orders(symbol=symbol, limit=limit)
            self.logger.info(f"Retrieved {len(orders)} orders from history")
            return orders
        except Exception as e:
            self.logger.error(f"Failed to get order history: {str(e)}")
            raise
