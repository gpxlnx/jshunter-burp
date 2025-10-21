# JSHunter Burp Suite Extension - Release Notes

## Version 2.0.0 - Telegram Integration

### 🚨 Breaking Changes

**Discord Integration Replaced with Telegram:**
- This version completely removes Discord webhook support
- All secret findings are now sent to Telegram instead of Discord
- Users need to configure a Telegram bot token and chat ID

### 🎉 What's New

**Telegram Bot Integration:**
- ✅ **Telegram Bot Support**: Send findings directly to Telegram channels/groups
- ✅ **Bot Token Configuration**: Easy setup with Telegram bot token from @BotFather
- ✅ **Chat ID Support**: Configure target channel or chat for notifications
- ✅ **Enhanced Formatting**: Messages include emojis for better visual distinction
  - 🔴 Red circle for verified secrets
  - 🟡 Yellow circle for unverified secrets
- ✅ **Markdown Support**: Rich text formatting in Telegram messages
- ✅ **Test Function**: Test Telegram configuration with a single click

**UI Updates:**
- ✅ **New Configuration Fields**: Separate fields for Bot Token and Chat ID
- ✅ **Updated Checkbox**: "Send findings to Telegram" replaces Discord option
- ✅ **Test Button**: Dedicated button to test Telegram connection

### 🔧 Migration Guide

**For existing users migrating from version 1.0.0:**

1. **Create a Telegram Bot:**
   - Open Telegram and search for [@BotFather](https://t.me/BotFather)
   - Send `/newbot` command and follow the instructions
   - Save the bot token (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

2. **Get Your Chat ID:**
   - Add your bot to your channel as administrator
   - Send a test message to your channel
   - Visit `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find the `chat` object and copy the `id` field (may be negative for channels)

3. **Configure JSHunter:**
   - Open JSHunter tab in Burp Suite
   - Enter your Bot Token in the "Telegram Bot Token" field
   - Enter your Chat ID in the "Telegram Chat ID" field
   - Click "Test" to verify the connection
   - Enable "Send findings to Telegram" checkbox

### 📋 Telegram Message Format

**Verified Secrets:**
```
🔴 *[VERIFIED] Verified Secrets*
Found in: `https://example.com/script.js`

*GitHub Token*
```
ghp_***REDACTED***
```
Line: 42
```

**Unverified Secrets:**
```
🟡 *[UNVERIFIED] Unverified Secrets*
Found in: `https://example.com/script.js`

*API Key*
```
api_key: "***REDACTED***"
```
Line: 15
```

### 🎯 Why Telegram?

- **Better Privacy**: Self-hosted bots with full control
- **More Flexibility**: Support for channels, groups, and private chats
- **Rich Formatting**: Better markdown support and emoji integration
- **API Access**: Easier programmatic access to messages
- **No Webhook Limitations**: More reliable message delivery

### 📝 Settings Changes

| Old Setting (1.0.0) | New Setting (2.0.0) |
|---------------------|---------------------|
| Discord Webhook URL | Telegram Bot Token |
| *(none)* | Telegram Chat ID |
| Send findings to Discord | Send findings to Telegram |
| Test Discord button | Test Telegram button |

### 🛠️ Technical Changes

- Replaced `_discord_webhook_url` with `_telegram_bot_token` and `_telegram_chat_id`
- Replaced `_send_to_discord_enabled` with `_send_to_telegram_enabled`
- Updated HTTP POST requests to use Telegram Bot API instead of Discord webhooks
- Changed message formatting to use Markdown instead of Discord formatting
- Updated all event listeners and UI components

### 📋 Requirements

- **Burp Suite**: Professional or Community Edition
- **Python**: Python 2.7 (comes with Burp Suite's Jython)
- **TruffleHog**: TruffleHog binary installed and accessible
- **Telegram Bot**: Bot token from @BotFather
- **Telegram Channel/Chat**: Chat ID for receiving notifications

### 🚀 What's Maintained

All core features remain unchanged:
- ✅ Automatic JavaScript URL detection
- ✅ TruffleHog integration for secret scanning
- ✅ Live results display
- ✅ Resizable UI panels
- ✅ Persistent settings
- ✅ Automatic file cleanup
- ✅ Comprehensive error handling

---

## Version 1.0.0 - Initial Release

### 🎉 What's New

**Core Features:**
- ✅ **Automatic JavaScript URL Detection**: Monitors HTTP traffic and automatically identifies JavaScript files
- ✅ **TruffleHog Integration**: Scans JavaScript files for secrets using the powerful TruffleHog tool
- ✅ **Discord Webhook Support**: Sends findings directly to Discord channels for real-time notifications
- ✅ **Live Results Display**: Shows scan results and findings in a clean, organized interface

**UI Features:**
- ✅ **Resizable Panels**: Adjustable panel sizes for better workflow
- ✅ **Comprehensive Settings**: Configure TruffleHog path, Discord webhook, and scanning behavior
- ✅ **Findings Table**: Detailed view of detected secrets with type, URL, line number, and verification status
- ✅ **Statistics Dashboard**: Shows total findings, verified secrets, and scanned URLs

**Technical Features:**
- ✅ **Persistent Settings**: Settings are saved across Burp Suite sessions
- ✅ **Automatic Cleanup**: Temporary files are automatically cleaned up after scanning
- ✅ **Error Handling**: Comprehensive error handling and user feedback
- ✅ **File Browser**: Easy TruffleHog binary path selection
- ✅ **Test Functions**: Test TruffleHog and Discord webhook configurations

### 🔧 Installation

1. **Download**: Get `jshunter_extension.py` from the repository
2. **Install in Burp Suite**: 
   - Go to **Extensions** → **Extensions**
   - Click **Add** → **Extension type: Python**
   - Select `jshunter_extension.py`
3. **Configure**: Set TruffleHog path and Discord webhook URL
4. **Start Scanning**: The extension automatically monitors HTTP traffic

### 📋 Requirements

- **Burp Suite**: Professional or Community Edition
- **Python**: Python 2.7 (comes with Burp Suite's Jython)
- **TruffleHog**: TruffleHog binary installed and accessible

### 🚀 Usage

1. **Automatic Monitoring**: The extension automatically detects JavaScript URLs in HTTP traffic
2. **Real-time Scanning**: Downloads and scans JavaScript files using TruffleHog
3. **Discord Notifications**: Sends formatted alerts to Discord webhooks
4. **Results Display**: View detailed findings in the JSHunter interface

### 🎯 Supported Secret Types

- **API Keys**: Various API key patterns
- **Tokens**: Authentication tokens and bearer tokens
- **Passwords**: Password and secret patterns
- **Private Keys**: RSA and SSH private keys
- **And more**: All patterns supported by TruffleHog

### 🔍 Discord Integration

The extension sends formatted messages to Discord:

**Verified Secrets:**
```
**[VERIFIED] Verified Secrets** found in https://example.com/script.js

**GitHub Token**
```
ghp_***REDACTED***
```
Line: 42
```

**Unverified Secrets:**
```
**[UNVERIFIED] Unverified Secrets** found in https://example.com/script.js

**API Key**
```
api_key: "***REDACTED***"
```
Line: 15
```

### 🛠️ Technical Details

- **Language**: Python 2.7 (Jython)
- **UI Framework**: Java Swing
- **HTTP Monitoring**: Burp Suite IHttpListener
- **Secret Scanning**: TruffleHog binary integration
- **Discord Integration**: HTTP POST requests to webhooks
- **File Management**: Automatic temporary file cleanup

### 📁 Repository Structure

```
jshunter-burp/
├── jshunter_extension.py    # Main extension file
├── README.md               # Comprehensive documentation
├── INSTALLATION.md         # Detailed installation guide
├── LICENSE                 # MIT License
├── .gitignore             # Git ignore rules
└── push-to-github.sh      # GitHub push helper script
```

### 🎉 What's Next

Future versions may include:
- Enhanced secret detection patterns
- Custom regex pattern support
- Integration with other security tools
- Advanced filtering options
- Performance optimizations

### 📞 Support

- **Issues**: [GitHub Issues](https://github.com/iamunixtz/jshunter-burp/issues)
- **Documentation**: [README.md](README.md)
- **Installation**: [INSTALLATION.md](INSTALLATION.md)

---

**Happy Hunting! 🎯**
