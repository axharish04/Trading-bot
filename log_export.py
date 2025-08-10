#!/usr/bin/env python3
"""
Log Export Utility for Binance Trading Bot
Exports and compresses log files for sharing via email
"""

import os
import zipfile
import datetime
from pathlib import Path
import shutil

class LogExporter:
    def __init__(self, logs_dir="logs"):
        """Initialize the log exporter
        
        Args:
            logs_dir: Directory containing log files
        """
        self.logs_dir = Path(logs_dir)
        self.export_dir = Path("exported_logs")
        
    def create_export_package(self, days=7):
        """Create a compressed package of recent log files
        
        Args:
            days: Number of days of logs to include (default: 7)
            
        Returns:
            str: Path to the created zip file
        """
        # Create export directory
        self.export_dir.mkdir(exist_ok=True)
        
        # Generate timestamp for filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"trading_bot_logs_{timestamp}.zip"
        zip_path = self.export_dir / zip_filename
        
        # Calculate cutoff date
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            log_count = 0
            
            # Add recent log files
            if self.logs_dir.exists():
                for log_file in self.logs_dir.glob("*.log"):
                    # Check file modification time
                    file_time = datetime.datetime.fromtimestamp(log_file.stat().st_mtime)
                    
                    if file_time > cutoff_date:
                        zipf.write(log_file, log_file.name)
                        log_count += 1
            
            # Add system info
            system_info = self._generate_system_info()
            zipf.writestr("system_info.txt", system_info)
            
            # Add README for the log package
            readme_content = self._generate_log_readme(days, log_count)
            zipf.writestr("LOG_README.txt", readme_content)
        
        return str(zip_path)
    
    def _generate_system_info(self):
        """Generate system information for troubleshooting"""
        import platform
        import sys
        
        info = [
            f"Trading Bot Log Export",
            f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "System Information:",
            f"Python Version: {sys.version}",
            f"Platform: {platform.platform()}",
            f"Architecture: {platform.architecture()[0]}",
            "",
            "Log Files Included:",
        ]
        
        if self.logs_dir.exists():
            for log_file in sorted(self.logs_dir.glob("*.log")):
                size_kb = log_file.stat().st_size / 1024
                mod_time = datetime.datetime.fromtimestamp(log_file.stat().st_mtime)
                info.append(f"  {log_file.name} - {size_kb:.1f}KB - {mod_time.strftime('%Y-%m-%d %H:%M')}")
        
        return "\n".join(info)
    
    def _generate_log_readme(self, days, log_count):
        """Generate README for log package"""
        content = f"""Binance Trading Bot - Log Files Export
=====================================

Export Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Log Period: Last {days} days
Files Included: {log_count} log files

Contents:
---------
- system_info.txt: System and environment information
- *.log files: Trading bot activity logs
- This README file

Usage:
------
These log files contain detailed information about trading bot activities:
- API requests and responses
- Order placements and executions
- Error messages and debugging information
- System performance metrics

For Support:
-----------
When reporting issues, please include:
1. Clear description of the problem
2. Steps to reproduce (if applicable)
3. These log files
4. System information from system_info.txt

Privacy Notice:
--------------
These logs may contain:
- Trading activities and timestamps
- API response data (symbols, prices, quantities)
- System performance information

These logs do NOT contain:
- API keys or secrets
- Personal account information
- Sensitive authentication data

File Format:
-----------
Log files follow the format: YYYY-MM-DD HH:MM:SS - Module - Level - Message
"""
        return content
    
    def clean_old_exports(self, keep_days=30):
        """Clean old export files
        
        Args:
            keep_days: Number of days to keep export files
        """
        if not self.export_dir.exists():
            return
        
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=keep_days)
        
        for export_file in self.export_dir.glob("trading_bot_logs_*.zip"):
            file_time = datetime.datetime.fromtimestamp(export_file.stat().st_mtime)
            if file_time < cutoff_date:
                export_file.unlink()
                print(f"Cleaned old export: {export_file.name}")

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Export trading bot logs for sharing")
    parser.add_argument("--days", type=int, default=7, 
                       help="Number of days of logs to include (default: 7)")
    parser.add_argument("--clean", action="store_true", 
                       help="Clean old export files")
    
    args = parser.parse_args()
    
    exporter = LogExporter()
    
    if args.clean:
        exporter.clean_old_exports()
        print("Cleaned old export files")
        return
    
    try:
        zip_path = exporter.create_export_package(days=args.days)
        file_size = os.path.getsize(zip_path) / 1024  # Size in KB
        
        print(f"\n✅ Log export created successfully!")
        print(f"📁 File: {zip_path}")
        print(f"📊 Size: {file_size:.1f} KB")
        print(f"📅 Period: Last {args.days} days")
        print(f"\nYou can now attach this file to your email.")
        
        # Show email template
        print(f"\n" + "="*50)
        print("EMAIL TEMPLATE:")
        print("="*50)
        print(f"""Subject: Trading Bot Logs - {datetime.datetime.now().strftime('%Y-%m-%d')}

Dear Support Team,

Please find attached the trading bot log files for analysis.

Log Details:
- Export Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Period: Last {args.days} days
- File: {os.path.basename(zip_path)}

Issue Description:
[Please describe your issue here]

Best regards,
[Your Name]""")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Error creating log export: {e}")

if __name__ == "__main__":
    main()
