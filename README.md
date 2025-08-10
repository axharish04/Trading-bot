# Binance Futures Trading Bot

Advanced algorithmic trading system with professional CLI interface and comprehensive risk management for Binance Futures Testnet.

## Overview

This project implements a sophisticated trading bot designed for Binance Futures Testnet, featuring advanced trading strategies, real-time market data integration, and comprehensive logging capabilities. Built with enterprise-grade architecture following professional development standards.

### Key Features

- Professional-grade code structure and documentation
- Real-time trading with live market data integration
- Advanced trading algorithms: TWAP and Grid Trading strategies
- Comprehensive risk management and error handling
- Interactive command-line interface with real-time updates
- Complete audit trail with detailed logging system

## Core Trading Capabilities

### Basic Order Types
- Market Orders (Buy/Sell)
- Limit Orders (Buy/Sell)
- Stop-Limit Orders
- OCO Orders (One-Cancels-Other)

### Advanced Trading Strategies
- TWAP Orders (Time-Weighted Average Price)
- Grid Trading Bot with configurable parameters
- Multi-timeframe support

### Account Management
- Real-time balance checking
- Order history and status tracking
- Open orders management
- Position monitoring

## Prerequisites

### Binance Testnet Account
1. Register at [Binance Futures Testnet](https://testnet.binancefuture.com/)
2. Complete email verification
3. Navigate to API Management
4. Create new API key with futures trading permissions
5. Securely store your API Key and Secret Key

### Technical Requirements
- Python 3.8 or higher
- pip package installer
- Stable internet connection

## Installation

### 1. Environment Setup
```bash
git clone https://github.com/axharish04/binance-futures-trading-bot.git
cd binance-futures-trading-bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory:
```env
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_SECRET_KEY=your_testnet_secret_key_here
```

## Usage

### Starting the Trading Bot
```bash
python main.py
```

### Interactive Menu Options
1. **Account Information** - View balance and account details
2. **Market Data** - Real-time price information
3. **Basic Trading** - Market and limit orders
4. **Advanced Orders** - Stop-limit and OCO orders
5. **Trading Strategies** - TWAP and Grid trading
6. **Order Management** - View and cancel orders

### Example Trading Session
```
Welcome to Binance Futures Trading Bot
====================================

Current Balance: 15000.00 USDT
Available Symbols: BTCUSDT, ETHUSDT, ADAUSDT...

Select Trading Option:
[1] Place Market Order
[2] Place Limit Order
[3] TWAP Strategy
[4] Grid Trading Bot

Enter your choice: 1
```

## Project Structure

```
primetrade/
├── main.py              # Interactive CLI application
├── trading_bot.py       # Core trading logic and API integration
├── advanced_bots.py     # TWAP and Grid trading strategies
├── config.py            # Configuration management
├── logger.py            # Comprehensive logging system
├── requirements.txt     # Python dependencies
└── logs/               # Trading activity logs
```

## Configuration

### Environment Variables
- `BINANCE_API_KEY`: Your Binance Testnet API key
- `BINANCE_SECRET_KEY`: Your Binance Testnet secret key

### Customizable Parameters
- Trading symbols and pairs
- Order quantities and price levels
- TWAP execution timeframes
- Grid trading parameters
- Logging levels and output formats

## Logging and Monitoring

The bot maintains comprehensive logs of all activities:
- API requests and responses
- Order placements and executions
- Error handling and recovery
- Trading strategy performance
- Account balance changes

Log files are stored in the `logs/` directory with timestamp-based naming.

### Sharing Log Files for Support

The bot includes a log export utility for easy sharing of log files via email:

```bash
# Export last 7 days of logs (default)
python log_export.py

# Export last 30 days of logs
python log_export.py --days 30

# Windows users can also use:
export_logs.bat
```

This creates a compressed ZIP file in the `exported_logs/` directory containing:
- Recent log files (sanitized of sensitive data)
- System information for troubleshooting
- Usage instructions and documentation

The exported logs are safe to share as they contain no API keys or personal information.

## Risk Management

### Built-in Safety Features
- Input validation for all trading parameters
- Confirmation prompts for order placement
- Error handling for API connectivity issues
- Automatic time synchronization with Binance servers
- Position size validation

### Best Practices
- Start with small position sizes
- Monitor market conditions closely
- Use stop-loss orders appropriately
- Review trading logs regularly

## Development

### Code Architecture
- **Modular Design**: Separate modules for different functionalities
- **Error Handling**: Comprehensive exception management
- **Logging**: Detailed activity tracking
- **Configuration**: Environment-based settings management

### Testing
The bot includes comprehensive error handling and validation:
- API connectivity verification
- Parameter validation
- Order execution confirmation
- Balance verification

## Technical Specifications

### Dependencies
- python-binance: Official Binance API wrapper
- colorama: Cross-platform colored terminal output
- tabulate: ASCII table formatting
- prompt-toolkit: Interactive command-line interface
- python-dotenv: Environment variable management

### Performance
- Real-time market data processing
- Efficient API request management
- Optimized order execution
- Minimal latency trading operations

## Security Considerations

- API credentials stored in environment variables
- No hardcoded sensitive information
- Secure API key management
- Network security best practices

## Contributing

This project follows professional development standards:
- Clean, documented code
- Modular architecture
- Comprehensive error handling
- Detailed logging

## License

This project is developed for educational and testing purposes on Binance Futures Testnet.

## Disclaimer

This software is for educational and testing purposes only. Use at your own risk. Trading involves substantial risk of loss and is not suitable for all investors. Always test thoroughly before any real trading activities.

---

**Note**: This bot is designed specifically for Binance Futures Testnet and should not be used with real funds without proper testing and risk assessment.
