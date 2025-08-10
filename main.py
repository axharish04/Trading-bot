import os
import sys
from typing import Dict, List, Optional
from colorama import Fore, Style, init
from tabulate import tabulate
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import confirm
from prompt_toolkit.validation import Validator, ValidationError
import json

# Initialize colorama
init(autoreset=True)

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from trading_bot import BasicBot
from advanced_bots import TWAPBot, GridBot
from logger import Logger

class FloatValidator(Validator):
    """Validator for float input"""
    def validate(self, document):
        try:
            float(document.text)
        except ValueError:
            raise ValidationError(message="Please enter a valid number")

class IntValidator(Validator):
    """Validator for integer input"""
    def validate(self, document):
        try:
            int(document.text)
        except ValueError:
            raise ValidationError(message="Please enter a valid integer")

class TradingBotCLI:
    """Command-line interface for the trading bot"""
    
    def __init__(self):
        self.logger = Logger("CLI")
        self.bot = None
        self.twap_bot = None
        self.grid_bot = None
        self.current_symbol = Config.DEFAULT_SYMBOL
        
        # Display banner
        self._display_banner()
        
        # Initialize bot
        self._initialize_bot()
    
    def _display_banner(self):
        """Display application banner"""
        banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗
║                           BINANCE FUTURES TRADING BOT                        ║
║                                  TESTNET MODE                                ║
╚══════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.YELLOW}⚠️  WARNING: This is a testnet environment. No real money is involved.{Style.RESET_ALL}
{Fore.GREEN}✅ Features: Market Orders, Limit Orders, Stop-Limit Orders, OCO Orders, TWAP, Grid Trading{Style.RESET_ALL}

"""
        print(banner)
    
    def _initialize_bot(self):
        """Initialize the trading bot"""
        try:
            # Validate configuration
            Config.validate_config()
            
            # Initialize bots
            self.bot = BasicBot(Config.API_KEY, Config.API_SECRET, testnet=True)
            self.twap_bot = TWAPBot(Config.API_KEY, Config.API_SECRET, testnet=True)
            self.grid_bot = GridBot(Config.API_KEY, Config.API_SECRET, testnet=True)
            
            # Get and display account info
            balance = self.bot.get_balance()
            print(f"{Fore.GREEN}✅ Bot initialized successfully!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}💰 Current USDT Balance: {balance:.2f} USDT{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to initialize bot: {str(e)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}💡 Please check your .env file and API credentials.{Style.RESET_ALL}")
            sys.exit(1)
    
    def _get_user_input(self, prompt_text: str, validator=None, default=None) -> str:
        """Get validated user input"""
        try:
            if default:
                prompt_text += f" (default: {default})"
            prompt_text += ": "
            
            result = prompt(prompt_text, validator=validator)
            return result if result else default
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Operation cancelled by user.{Style.RESET_ALL}")
            return None
    
    def _display_menu(self):
        """Display main menu"""
        menu = f"""
{Fore.CYAN}═══════════════════════════════════════════════════════════════════════════════
                                 MAIN MENU
═══════════════════════════════════════════════════════════════════════════════{Style.RESET_ALL}

{Fore.GREEN}📊 ACCOUNT & INFO{Style.RESET_ALL}
  [1] View Account Balance
  [2] Get Current Price
  [3] View Open Orders
  [4] View Order History

{Fore.BLUE}📈 BASIC TRADING{Style.RESET_ALL}
  [5] Place Market Order
  [6] Place Limit Order
  [7] Place Stop-Limit Order

{Fore.MAGENTA}🚀 ADVANCED TRADING{Style.RESET_ALL}
  [8] Place OCO Order
  [9] Execute TWAP Order
  [10] Setup Grid Trading

{Fore.YELLOW}⚙️  MANAGEMENT{Style.RESET_ALL}
  [11] Cancel Order
  [12] Cancel All Orders
  [13] Change Trading Symbol

{Fore.RED}🚪 EXIT{Style.RESET_ALL}
  [0] Exit Application

{Fore.CYAN}═══════════════════════════════════════════════════════════════════════════════{Style.RESET_ALL}
"""
        print(menu)
        print(f"{Fore.YELLOW}Current Symbol: {self.current_symbol}{Style.RESET_ALL}")
    
    def _view_balance(self):
        """Display account balance"""
        try:
            balance = self.bot.get_balance()
            account_info = self.bot.account_info
            
            if account_info:
                print(f"\n{Fore.GREEN}📊 ACCOUNT INFORMATION{Style.RESET_ALL}")
                print(f"{'─' * 50}")
                print(f"💰 Wallet Balance: {float(account_info['totalWalletBalance']):.2f} USDT")
                print(f"💸 Available Balance: {balance:.2f} USDT")
                print(f"📈 Unrealized PNL: {float(account_info['totalUnrealizedProfit']):.2f} USDT")
                print(f"🔒 Total Margin Balance: {float(account_info['totalMarginBalance']):.2f} USDT")
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to get balance: {str(e)}{Style.RESET_ALL}")
    
    def _get_current_price(self):
        """Get and display current price"""
        try:
            symbol = self._get_user_input("Enter symbol", default=self.current_symbol)
            if not symbol:
                return
                
            price = self.bot.get_current_price(symbol.upper())
            print(f"\n{Fore.GREEN}💰 Current Price for {symbol.upper()}: {price:.6f} USDT{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to get price: {str(e)}{Style.RESET_ALL}")
    
    def _place_market_order(self):
        """Place a market order"""
        try:
            print(f"\n{Fore.BLUE}📈 PLACE MARKET ORDER{Style.RESET_ALL}")
            
            symbol = self._get_user_input("Enter symbol", default=self.current_symbol)
            if not symbol:
                return
            
            side = self._get_user_input("Enter side (BUY/SELL)").upper()
            if side not in ['BUY', 'SELL']:
                print(f"{Fore.RED}❌ Invalid side. Must be BUY or SELL.{Style.RESET_ALL}")
                return
            
            quantity = float(self._get_user_input("Enter quantity", validator=FloatValidator()))
            
            # Show confirmation
            current_price = self.bot.get_current_price(symbol.upper())
            estimated_cost = quantity * current_price
            
            print(f"\n{Fore.YELLOW}📋 ORDER SUMMARY{Style.RESET_ALL}")
            print(f"Symbol: {symbol.upper()}")
            print(f"Side: {side}")
            print(f"Quantity: {quantity}")
            print(f"Type: MARKET")
            print(f"Current Price: {current_price:.6f}")
            print(f"Estimated Cost: {estimated_cost:.2f} USDT")
            
            if confirm("Confirm order placement?"):
                order = self.bot.place_market_order(symbol.upper(), side, quantity)
                self._display_order_result(order)
            else:
                print(f"{Fore.YELLOW}Order cancelled.{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to place market order: {str(e)}{Style.RESET_ALL}")
    
    def _place_limit_order(self):
        """Place a limit order"""
        try:
            print(f"\n{Fore.BLUE}📊 PLACE LIMIT ORDER{Style.RESET_ALL}")
            
            symbol = self._get_user_input("Enter symbol", default=self.current_symbol)
            if not symbol:
                return
            
            side = self._get_user_input("Enter side (BUY/SELL)").upper()
            if side not in ['BUY', 'SELL']:
                print(f"{Fore.RED}❌ Invalid side. Must be BUY or SELL.{Style.RESET_ALL}")
                return
            
            quantity = float(self._get_user_input("Enter quantity", validator=FloatValidator()))
            
            # Show current price for reference
            current_price = self.bot.get_current_price(symbol.upper())
            print(f"Current market price: {current_price:.6f}")
            
            price = float(self._get_user_input("Enter limit price", validator=FloatValidator()))
            
            time_in_force = self._get_user_input("Enter time in force (GTC/IOC/FOK)", default="GTC").upper()
            if time_in_force not in ['GTC', 'IOC', 'FOK']:
                time_in_force = 'GTC'
            
            # Show confirmation
            estimated_cost = quantity * price
            
            print(f"\n{Fore.YELLOW}📋 ORDER SUMMARY{Style.RESET_ALL}")
            print(f"Symbol: {symbol.upper()}")
            print(f"Side: {side}")
            print(f"Quantity: {quantity}")
            print(f"Type: LIMIT")
            print(f"Price: {price:.6f}")
            print(f"Time in Force: {time_in_force}")
            print(f"Estimated Cost: {estimated_cost:.2f} USDT")
            
            if confirm("Confirm order placement?"):
                order = self.bot.place_limit_order(symbol.upper(), side, quantity, price, time_in_force)
                self._display_order_result(order)
            else:
                print(f"{Fore.YELLOW}Order cancelled.{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to place limit order: {str(e)}{Style.RESET_ALL}")
    
    def _place_stop_limit_order(self):
        """Place a stop-limit order"""
        try:
            print(f"\n{Fore.MAGENTA}🛑 PLACE STOP-LIMIT ORDER{Style.RESET_ALL}")
            
            symbol = self._get_user_input("Enter symbol", default=self.current_symbol)
            if not symbol:
                return
            
            side = self._get_user_input("Enter side (BUY/SELL)").upper()
            if side not in ['BUY', 'SELL']:
                print(f"{Fore.RED}❌ Invalid side. Must be BUY or SELL.{Style.RESET_ALL}")
                return
            
            quantity = float(self._get_user_input("Enter quantity", validator=FloatValidator()))
            
            # Show current price for reference
            current_price = self.bot.get_current_price(symbol.upper())
            print(f"Current market price: {current_price:.6f}")
            
            stop_price = float(self._get_user_input("Enter stop price (trigger)", validator=FloatValidator()))
            limit_price = float(self._get_user_input("Enter limit price (execution)", validator=FloatValidator()))
            
            # Show confirmation
            print(f"\n{Fore.YELLOW}📋 ORDER SUMMARY{Style.RESET_ALL}")
            print(f"Symbol: {symbol.upper()}")
            print(f"Side: {side}")
            print(f"Quantity: {quantity}")
            print(f"Type: STOP-LIMIT")
            print(f"Stop Price: {stop_price:.6f}")
            print(f"Limit Price: {limit_price:.6f}")
            
            if confirm("Confirm order placement?"):
                order = self.bot.place_stop_limit_order(symbol.upper(), side, quantity, stop_price, limit_price)
                self._display_order_result(order)
            else:
                print(f"{Fore.YELLOW}Order cancelled.{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to place stop-limit order: {str(e)}{Style.RESET_ALL}")
    
    def _place_oco_order(self):
        """Place an OCO order"""
        try:
            print(f"\n{Fore.MAGENTA}🔄 PLACE OCO ORDER{Style.RESET_ALL}")
            print("OCO (One-Cancels-Other) orders help manage risk with take-profit and stop-loss")
            
            symbol = self._get_user_input("Enter symbol", default=self.current_symbol)
            if not symbol:
                return
            
            side = self._get_user_input("Enter side (BUY/SELL)").upper()
            if side not in ['BUY', 'SELL']:
                print(f"{Fore.RED}❌ Invalid side. Must be BUY or SELL.{Style.RESET_ALL}")
                return
            
            quantity = float(self._get_user_input("Enter quantity", validator=FloatValidator()))
            
            # Show current price for reference
            current_price = self.bot.get_current_price(symbol.upper())
            print(f"Current market price: {current_price:.6f}")
            
            price = float(self._get_user_input("Enter limit price", validator=FloatValidator()))
            stop_price = float(self._get_user_input("Enter stop price", validator=FloatValidator()))
            stop_limit_price = float(self._get_user_input("Enter stop limit price", validator=FloatValidator()))
            
            # Show confirmation
            print(f"\n{Fore.YELLOW}📋 OCO ORDER SUMMARY{Style.RESET_ALL}")
            print(f"Symbol: {symbol.upper()}")
            print(f"Side: {side}")
            print(f"Quantity: {quantity}")
            print(f"Limit Price: {price:.6f}")
            print(f"Stop Price: {stop_price:.6f}")
            print(f"Stop Limit Price: {stop_limit_price:.6f}")
            
            if confirm("Confirm OCO order placement?"):
                result = self.bot.place_oco_order(symbol.upper(), side, quantity, price, stop_price, stop_limit_price)
                print(f"\n{Fore.GREEN}✅ OCO Order placed successfully!{Style.RESET_ALL}")
                print(f"Limit Order ID: {result['limitOrder']['orderId']}")
                print(f"Stop Order ID: {result['stopOrder']['orderId']}")
            else:
                print(f"{Fore.YELLOW}OCO Order cancelled.{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to place OCO order: {str(e)}{Style.RESET_ALL}")
    
    def _execute_twap_order(self):
        """Execute a TWAP order"""
        try:
            print(f"\n{Fore.MAGENTA}⏰ EXECUTE TWAP ORDER{Style.RESET_ALL}")
            print("TWAP (Time-Weighted Average Price) spreads large orders over time")
            
            symbol = self._get_user_input("Enter symbol", default=self.current_symbol)
            if not symbol:
                return
            
            side = self._get_user_input("Enter side (BUY/SELL)").upper()
            if side not in ['BUY', 'SELL']:
                print(f"{Fore.RED}❌ Invalid side. Must be BUY or SELL.{Style.RESET_ALL}")
                return
            
            total_quantity = float(self._get_user_input("Enter total quantity", validator=FloatValidator()))
            duration_minutes = int(self._get_user_input("Enter duration in minutes", validator=IntValidator()))
            num_intervals = int(self._get_user_input("Enter number of intervals", default="10", validator=IntValidator()))
            
            # Show confirmation
            quantity_per_interval = total_quantity / num_intervals
            interval_seconds = (duration_minutes * 60) / num_intervals
            
            print(f"\n{Fore.YELLOW}📋 TWAP ORDER SUMMARY{Style.RESET_ALL}")
            print(f"Symbol: {symbol.upper()}")
            print(f"Side: {side}")
            print(f"Total Quantity: {total_quantity}")
            print(f"Duration: {duration_minutes} minutes")
            print(f"Number of Intervals: {num_intervals}")
            print(f"Quantity per Interval: {quantity_per_interval:.6f}")
            print(f"Interval Duration: {interval_seconds:.1f} seconds")
            
            if confirm("Start TWAP execution?"):
                orders = self.twap_bot.execute_twap_order(
                    symbol.upper(), side, total_quantity, duration_minutes, num_intervals
                )
                print(f"\n{Fore.GREEN}✅ TWAP order execution completed!{Style.RESET_ALL}")
                print(f"Executed {len(orders)} orders")
            else:
                print(f"{Fore.YELLOW}TWAP order cancelled.{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to execute TWAP order: {str(e)}{Style.RESET_ALL}")
    
    def _setup_grid_trading(self):
        """Setup grid trading"""
        try:
            print(f"\n{Fore.MAGENTA}📊 SETUP GRID TRADING{Style.RESET_ALL}")
            print("Grid trading places buy and sell orders at regular intervals around current price")
            
            symbol = self._get_user_input("Enter symbol", default=self.current_symbol)
            if not symbol:
                return
            
            # Get current price
            current_price = self.bot.get_current_price(symbol.upper())
            print(f"Current price: {current_price:.6f}")
            
            center_price = float(self._get_user_input("Enter center price", default=str(current_price), validator=FloatValidator()))
            grid_spacing = float(self._get_user_input("Enter grid spacing (%)", default="1.0", validator=FloatValidator()))
            num_grids = int(self._get_user_input("Enter number of grids above/below", default="5", validator=IntValidator()))
            quantity_per_grid = float(self._get_user_input("Enter quantity per grid", validator=FloatValidator()))
            
            # Calculate total required balance
            total_sell_value = sum(center_price * (1 + (grid_spacing / 100) * i) * quantity_per_grid for i in range(1, num_grids + 1))
            total_buy_value = sum(center_price * (1 - (grid_spacing / 100) * i) * quantity_per_grid for i in range(1, num_grids + 1))
            
            print(f"\n{Fore.YELLOW}📋 GRID TRADING SUMMARY{Style.RESET_ALL}")
            print(f"Symbol: {symbol.upper()}")
            print(f"Center Price: {center_price:.6f}")
            print(f"Grid Spacing: {grid_spacing}%")
            print(f"Number of Grids: {num_grids} above + {num_grids} below")
            print(f"Quantity per Grid: {quantity_per_grid}")
            print(f"Total Orders: {num_grids * 2}")
            print(f"Estimated USDT needed: {total_buy_value:.2f}")
            
            if confirm("Setup grid trading?"):
                orders = self.grid_bot.setup_grid(
                    symbol.upper(), center_price, grid_spacing, num_grids, quantity_per_grid
                )
                print(f"\n{Fore.GREEN}✅ Grid trading setup completed!{Style.RESET_ALL}")
                print(f"Placed {len(orders)} grid orders")
            else:
                print(f"{Fore.YELLOW}Grid trading setup cancelled.{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to setup grid trading: {str(e)}{Style.RESET_ALL}")
    
    def _view_open_orders(self):
        """View open orders"""
        try:
            orders = self.bot.get_open_orders()
            
            if not orders:
                print(f"\n{Fore.YELLOW}📭 No open orders found.{Style.RESET_ALL}")
                return
            
            # Prepare data for table
            table_data = []
            for order in orders:
                table_data.append([
                    order['orderId'],
                    order['symbol'],
                    order['side'],
                    order['type'],
                    f"{float(order['origQty']):.6f}",
                    f"{float(order['price']):.6f}" if order['price'] != '0' else 'MARKET',
                    order['status']
                ])
            
            print(f"\n{Fore.GREEN}📊 OPEN ORDERS{Style.RESET_ALL}")
            print(tabulate(
                table_data,
                headers=['Order ID', 'Symbol', 'Side', 'Type', 'Quantity', 'Price', 'Status'],
                tablefmt='grid'
            ))
            
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to get open orders: {str(e)}{Style.RESET_ALL}")
    
    def _view_order_history(self):
        """View order history"""
        try:
            symbol = self._get_user_input("Enter symbol", default=self.current_symbol)
            if not symbol:
                return
            
            limit = int(self._get_user_input("Number of orders to show", default="10", validator=IntValidator()))
            
            orders = self.bot.get_order_history(symbol.upper(), limit)
            
            if not orders:
                print(f"\n{Fore.YELLOW}📭 No order history found.{Style.RESET_ALL}")
                return
            
            # Prepare data for table
            table_data = []
            for order in orders[:limit]:
                table_data.append([
                    order['orderId'],
                    order['symbol'],
                    order['side'],
                    order['type'],
                    f"{float(order['origQty']):.6f}",
                    f"{float(order['avgPrice']):.6f}" if order.get('avgPrice') and order['avgPrice'] != '0' else 'N/A',
                    order['status']
                ])
            
            print(f"\n{Fore.GREEN}📊 ORDER HISTORY ({symbol.upper()}){Style.RESET_ALL}")
            print(tabulate(
                table_data,
                headers=['Order ID', 'Symbol', 'Side', 'Type', 'Quantity', 'Avg Price', 'Status'],
                tablefmt='grid'
            ))
            
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to get order history: {str(e)}{Style.RESET_ALL}")
    
    def _cancel_order(self):
        """Cancel a specific order"""
        try:
            symbol = self._get_user_input("Enter symbol", default=self.current_symbol)
            if not symbol:
                return
            
            order_id = int(self._get_user_input("Enter order ID to cancel", validator=IntValidator()))
            
            if confirm(f"Cancel order {order_id}?"):
                result = self.bot.cancel_order(symbol.upper(), order_id)
                print(f"\n{Fore.GREEN}✅ Order {order_id} cancelled successfully!{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}Cancellation aborted.{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to cancel order: {str(e)}{Style.RESET_ALL}")
    
    def _cancel_all_orders(self):
        """Cancel all open orders"""
        try:
            symbol = self._get_user_input("Enter symbol (leave empty for all symbols)", default="")
            
            if confirm("⚠️  Cancel ALL open orders? This cannot be undone!"):
                orders = self.bot.get_open_orders(symbol.upper() if symbol else None)
                
                cancelled_count = 0
                for order in orders:
                    try:
                        self.bot.cancel_order(order['symbol'], order['orderId'])
                        cancelled_count += 1
                    except:
                        continue
                
                print(f"\n{Fore.GREEN}✅ Cancelled {cancelled_count} orders successfully!{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}Cancellation aborted.{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to cancel orders: {str(e)}{Style.RESET_ALL}")
    
    def _change_symbol(self):
        """Change the current trading symbol"""
        try:
            new_symbol = self._get_user_input("Enter new symbol", default=self.current_symbol)
            if new_symbol:
                # Test if symbol exists by getting its price
                self.bot.get_current_price(new_symbol.upper())
                self.current_symbol = new_symbol.upper()
                print(f"{Fore.GREEN}✅ Trading symbol changed to {self.current_symbol}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Invalid symbol: {str(e)}{Style.RESET_ALL}")
    
    def _display_order_result(self, order: Dict):
        """Display order execution result"""
        print(f"\n{Fore.GREEN}✅ ORDER EXECUTED SUCCESSFULLY!{Style.RESET_ALL}")
        print(f"{'─' * 40}")
        print(f"Order ID: {order['orderId']}")
        print(f"Symbol: {order['symbol']}")
        print(f"Side: {order['side']}")
        print(f"Type: {order['type']}")
        print(f"Quantity: {order['origQty']}")
        print(f"Status: {order['status']}")
        
        if 'fills' in order and order['fills']:
            print(f"Executed Quantity: {order['executedQty']}")
            avg_price = sum(float(fill['price']) * float(fill['qty']) for fill in order['fills']) / float(order['executedQty'])
            print(f"Average Price: {avg_price:.6f}")
    
    def run(self):
        """Run the CLI application"""
        try:
            while True:
                self._display_menu()
                
                choice = self._get_user_input(f"\n{Fore.CYAN}Select option{Style.RESET_ALL}")
                
                if choice == '0':
                    print(f"\n{Fore.GREEN}👋 Thank you for using the Trading Bot!{Style.RESET_ALL}")
                    break
                elif choice == '1':
                    self._view_balance()
                elif choice == '2':
                    self._get_current_price()
                elif choice == '3':
                    self._view_open_orders()
                elif choice == '4':
                    self._view_order_history()
                elif choice == '5':
                    self._place_market_order()
                elif choice == '6':
                    self._place_limit_order()
                elif choice == '7':
                    self._place_stop_limit_order()
                elif choice == '8':
                    self._place_oco_order()
                elif choice == '9':
                    self._execute_twap_order()
                elif choice == '10':
                    self._setup_grid_trading()
                elif choice == '11':
                    self._cancel_order()
                elif choice == '12':
                    self._cancel_all_orders()
                elif choice == '13':
                    self._change_symbol()
                else:
                    print(f"{Fore.RED}❌ Invalid option. Please try again.{Style.RESET_ALL}")
                
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}👋 Application interrupted by user. Goodbye!{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}❌ Unexpected error: {str(e)}{Style.RESET_ALL}")
            self.logger.error(f"CLI error: {str(e)}")

def main():
    """Main entry point"""
    try:
        cli = TradingBotCLI()
        cli.run()
    except Exception as e:
        print(f"{Fore.RED}❌ Failed to start application: {str(e)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Make sure you have configured your .env file properly.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
