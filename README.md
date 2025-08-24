# MNGserver 🤖

A powerful and elegant Python script monitoring system with automatic restart capabilities and real-time statistics.

![MNGserver](https://img.shields.io/badge/Version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.6%2B-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

- **📊 Real-time Monitoring** - Monitor Python scripts with automatic restart on crash
- **📈 Live Statistics** - CPU and memory usage charts with 60-point history
- **🔔 Telegram Notifications** - Get instant alerts when scripts crash or restart
- **🎯 Smart Restart Logic** - Configurable maximum restart attempts
- **📝 Comprehensive Logging** - Detailed logs with timestamps and script names
- **🎨 Dark Theme UI** - Modern, professional dark interface
- **⚙️ Per-Script Settings** - Individual configuration for each monitored script

## 🚀 Installation

1. **Clone the repository:**
```bash
git clone https://github.com/Tool-xx/MNGserver.git
cd MNGserver
```

2. **Install required dependencies:**
```bash
pip install -r requirements.txt
```

## 📋 Requirements

- Python 3.6+
- PyQt5
- psutil
- requests

## 🎮 Usage

1. **Start the application:**
```bash
python mngserver.py
```

2. **Add scripts to monitor:**
   - Click "📁 Add Script" button
   - Select your Python script (.py file)

3. **Configure settings (optional):**
   - Select a script from the list
   - Go to "⚙️ Settings" tab
   - Adjust max restarts, check interval, and Telegram settings

4. **Start monitoring:**
   - Select a script
   - Click "▶️ Start Monitoring"

5. **View statistics:**
   - Switch to "📊 Statistics" tab to see real-time charts
   - Monitor CPU and memory usage

## ⚙️ Configuration

### Script Settings
- **Max Restarts**: Maximum number of automatic restart attempts (1-100)
- **Check Interval**: How often to check script status (1-300 seconds)
- **Telegram Notifications**: Enable/disable Telegram alerts

### Telegram Setup
1. Create a bot using [BotFather](https://t.me/BotFather)
2. Get your bot token
3. Get your chat ID (use @userinfobot or similar)
4. Enable Telegram notifications in script settings
5. Test the connection with "Test Telegram" button

## 📊 Interface Overview

### Left Panel
- Script list with status indicators (🟢 running / 🔴 stopped)
- Add script button
- GitHub repository link

### Main Tabs
- **📝 Logs**: Real-time logging with save/clear functionality
- **📊 Statistics**: System-wide stats and per-script charts
- **⚙️ Settings**: Individual script configuration (when script selected)

### Control Buttons
- **▶️ Start Monitoring**: Start monitoring selected script
- **⏹️ Stop Monitoring**: Stop monitoring selected script  
- **🗑️ Remove Script**: Remove script from monitoring list

## 🔧 Technical Details

### Monitoring Logic
- Scripts run as subprocesses
- Continuous health checks at configured intervals
- Automatic restart on crash (within restart limits)
- Graceful termination on application close

### Statistics Collection
- Real-time CPU usage monitoring
- Memory consumption tracking
- 60-point history for trend analysis
- System-wide resource monitoring

## 🎨 Theme

MNGserver features a modern dark theme with:
- Professional color scheme
- High contrast for readability
- Consistent styling across all elements
- Responsive design

## 📋 Supported Platforms

- Windows 10/11
- macOS 10.15+
- Linux (Ubuntu 18.04+, Fedora, etc.)

## 🤝 Contributing

We welcome contributions! Please feel free to:
- Report bugs and issues
- Suggest new features
- Submit pull requests
- Improve documentation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with PyQt5 for the modern interface
- Uses psutil for system monitoring
- Telegram Bot API for notifications

## 📞 Support

If you encounter any issues or have questions:
1. Check the logs for error messages
2. Ensure all dependencies are installed
3. Verify script paths are correct
4. Test Telegram configuration separately

---

**MNGserver** - Keep your Python scripts running smoothly! 🚀
