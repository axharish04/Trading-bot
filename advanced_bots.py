import time
import statistics
from typing import List, Dict
from trading_bot import BasicBot
from logger import Logger

class TWAPBot(BasicBot):
    """
    Time-Weighted Average Price (TWAP) Bot
    Executes large orders by splitting them into smaller chunks over time
    """
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        super().__init__(api_key, api_secret, testnet)
        self.twap_logger = Logger("TWAP_Bot")
    
    def execute_twap_order(self, symbol: str, side: str, total_quantity: float, 
                          duration_minutes: int, num_intervals: int = 10) -> List[Dict]:
        """
        Execute a TWAP order
        
        Args:
            symbol: Trading pair
            side: BUY or SELL
            total_quantity: Total quantity to trade
            duration_minutes: Total time to spread the order over
            num_intervals: Number of intervals to split the order into
            
        Returns:
            List of executed orders
        """
        try:
            # Calculate order parameters
            quantity_per_interval = total_quantity / num_intervals
            interval_seconds = (duration_minutes * 60) / num_intervals
            
            executed_orders = []
            
            self.twap_logger.info(f"Starting TWAP order: {side} {total_quantity} {symbol}")
            self.twap_logger.info(f"Split into {num_intervals} intervals of {quantity_per_interval} each")
            self.twap_logger.info(f"Interval duration: {interval_seconds} seconds")
            
            for i in range(num_intervals):
                try:
                    # Execute market order for this interval
                    order = self.place_market_order(symbol, side, quantity_per_interval)
                    executed_orders.append(order)
                    
                    self.twap_logger.info(f"TWAP Interval {i+1}/{num_intervals} completed")
                    
                    # Wait for next interval (except for the last one)
                    if i < num_intervals - 1:
                        time.sleep(interval_seconds)
                        
                except Exception as e:
                    self.twap_logger.error(f"TWAP interval {i+1} failed: {str(e)}")
                    continue
            
            # Calculate TWAP statistics
            self._log_twap_summary(executed_orders, symbol)
            
            return executed_orders
            
        except Exception as e:
            self.twap_logger.error(f"TWAP order failed: {str(e)}")
            raise
    
    def _log_twap_summary(self, orders: List[Dict], symbol: str):
        """Log TWAP execution summary"""
        if not orders:
            return
        
        try:
            total_qty = sum(float(order.get('executedQty', 0)) for order in orders)
            prices = [float(order.get('avgPrice', 0)) for order in orders if float(order.get('avgPrice', 0)) > 0]
            
            if prices:
                avg_price = statistics.mean(prices)
                self.twap_logger.info(f"TWAP Summary for {symbol}:")
                self.twap_logger.info(f"- Total executed quantity: {total_qty}")
                self.twap_logger.info(f"- Average execution price: {avg_price:.6f}")
                self.twap_logger.info(f"- Number of fills: {len(orders)}")
                self.twap_logger.info(f"- Success rate: {len([o for o in orders if o.get('status') == 'FILLED'])/len(orders)*100:.1f}%")
        
        except Exception as e:
            self.twap_logger.error(f"Failed to calculate TWAP summary: {str(e)}")


class GridBot(BasicBot):
    """
    Grid Trading Bot
    Places buy and sell orders in a grid pattern around current price
    """
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        super().__init__(api_key, api_secret, testnet)
        self.grid_logger = Logger("Grid_Bot")
        self.grid_orders = []
    
    def setup_grid(self, symbol: str, center_price: float, grid_spacing: float, 
                  num_grids: int, quantity_per_grid: float) -> List[Dict]:
        """
        Set up a grid of buy and sell orders
        
        Args:
            symbol: Trading pair
            center_price: Center price for the grid
            grid_spacing: Price spacing between grid levels (in percentage)
            num_grids: Number of grid levels above and below center
            quantity_per_grid: Quantity for each grid order
            
        Returns:
            List of placed orders
        """
        try:
            self.grid_logger.info(f"Setting up grid for {symbol}")
            self.grid_logger.info(f"Center price: {center_price}, Spacing: {grid_spacing}%, Grids: {num_grids}")
            
            grid_orders = []
            
            for i in range(1, num_grids + 1):
                # Calculate prices
                buy_price = center_price * (1 - (grid_spacing / 100) * i)
                sell_price = center_price * (1 + (grid_spacing / 100) * i)
                
                try:
                    # Place buy order below center
                    buy_order = self.place_limit_order(symbol, 'BUY', quantity_per_grid, buy_price)
                    grid_orders.append(buy_order)
                    
                    # Place sell order above center
                    sell_order = self.place_limit_order(symbol, 'SELL', quantity_per_grid, sell_price)
                    grid_orders.append(sell_order)
                    
                    self.grid_logger.info(f"Grid level {i}: BUY at {buy_price:.6f}, SELL at {sell_price:.6f}")
                    
                except Exception as e:
                    self.grid_logger.error(f"Failed to place grid level {i}: {str(e)}")
                    continue
            
            self.grid_orders = grid_orders
            self.grid_logger.info(f"Grid setup completed with {len(grid_orders)} orders")
            return grid_orders
            
        except Exception as e:
            self.grid_logger.error(f"Grid setup failed: {str(e)}")
            raise
    
    def cancel_all_grid_orders(self, symbol: str):
        """Cancel all grid orders"""
        try:
            cancelled_count = 0
            for order in self.grid_orders:
                try:
                    self.cancel_order(symbol, order['orderId'])
                    cancelled_count += 1
                except:
                    continue
            
            self.grid_logger.info(f"Cancelled {cancelled_count} grid orders")
            self.grid_orders = []
            
        except Exception as e:
            self.grid_logger.error(f"Failed to cancel grid orders: {str(e)}")
    
    def monitor_and_replace_grid(self, symbol: str, center_price: float, 
                               grid_spacing: float, quantity_per_grid: float):
        """
        Monitor grid orders and replace filled ones
        (This is a basic implementation - in production you'd want this to run continuously)
        """
        try:
            filled_orders = []
            
            for order in self.grid_orders:
                try:
                    status = self.get_order_status(symbol, order['orderId'])
                    if status['status'] == 'FILLED':
                        filled_orders.append(order)
                        self.grid_logger.info(f"Grid order {order['orderId']} filled")
                except:
                    continue
            
            # Replace filled orders
            for filled_order in filled_orders:
                try:
                    # Remove from tracking
                    self.grid_orders.remove(filled_order)
                    
                    # Place replacement order on opposite side
                    if filled_order['side'] == 'BUY':
                        # If buy was filled, place sell above current price
                        new_price = center_price * (1 + grid_spacing / 100)
                        new_order = self.place_limit_order(symbol, 'SELL', quantity_per_grid, new_price)
                    else:
                        # If sell was filled, place buy below current price
                        new_price = center_price * (1 - grid_spacing / 100)
                        new_order = self.place_limit_order(symbol, 'BUY', quantity_per_grid, new_price)
                    
                    self.grid_orders.append(new_order)
                    self.grid_logger.info(f"Replaced filled order with new order at {new_price:.6f}")
                    
                except Exception as e:
                    self.grid_logger.error(f"Failed to replace filled order: {str(e)}")
            
        except Exception as e:
            self.grid_logger.error(f"Grid monitoring failed: {str(e)}")
