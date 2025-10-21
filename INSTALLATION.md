# JSHunter Burp Suite Extension - Installation Guide

## Quick Installation

1. **Download the Extension**: Get `jshunter_extension.py` from this repository
2. **Open Burp Suite**: Launch Burp Suite Professional or Community
3. **Go to Extensions**: Navigate to **Extensions** → **Extensions**
4. **Add Extension**: Click **Add** → **Extension type: Python**
5. **Select File**: Choose `jshunter_extension.py`
6. **Install**: Click **Next** and the extension will be loaded

## Prerequisites

### Burp Suite
- **Burp Suite Professional** (recommended) or **Burp Suite Community**
- Python support enabled (comes with Jython)

### TruffleHog Installation

**macOS:**
```bash
brew install trufflehog
```

**Linux:**
```bash
# Download the latest release
curl -L https://github.com/trufflesecurity/trufflehog/releases/latest/download/trufflehog_3.63.7_linux_amd64.tar.gz | tar -xz
sudo mv trufflehog /usr/local/bin/
```

**Windows:**
```bash
# Using Chocolatey
choco install trufflehog

# Or download from GitHub releases
```

### Telegram Bot Setup

1. **Create a Bot:**
   - Open Telegram and search for [@BotFather](https://t.me/BotFather)
   - Send `/newbot` command
   - Follow the instructions to create your bot
   - Save the bot token (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

2. **Get Chat ID:**
   - Create a channel or group for notifications (or use an existing one)
   - Add your bot to the channel as administrator
   - Send a test message to your channel
   - Visit `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find the `chat` object in the JSON response
   - Copy the `id` field (may be negative for channels)

## Step-by-Step Installation

### Step 1: Download the Extension
```bash
# Clone the repository
git clone https://github.com/yourusername/jshunter-burp.git
cd jshunter-burp

# Or download just the extension file
wget https://raw.githubusercontent.com/yourusername/jshunter-burp/main/jshunter_extension.py
```

### Step 2: Install in Burp Suite

1. **Open Burp Suite**
2. **Navigate to Extensions**:
   - Go to **Extensions** tab
   - Click **Extensions** in the left sidebar
3. **Add New Extension**:
   - Click **Add** button
   - Select **Extension type: Python**
4. **Select Extension File**:
   - Click **Select file...**
   - Navigate to and select `jshunter_extension.py`
5. **Load Extension**:
   - Click **Next**
   - The extension should load successfully
   - You should see "JSHunter" tab appear in the interface

### Step 3: Configure the Extension

1. **Open JSHunter Tab**: Click on the "JSHunter" tab
2. **Set TruffleHog Path**: 
   - Enter the path to your TruffleHog binary
   - Default: `/usr/local/bin/trufflehog`
   - Use the "Browse" button to find the file
3. **Test TruffleHog**: Click "Test" button to verify TruffleHog is working
4. **Set Telegram Bot Token**: Enter your Telegram bot token from @BotFather
5. **Set Telegram Chat ID**: Enter your channel/chat ID
6. **Test Telegram**: Click "Test" button next to Chat ID to verify connection
7. **Enable Features**: Check "Send findings to Telegram" if you want automatic notifications

## Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| TruffleHog Path | Path to TruffleHog executable | `/usr/local/bin/trufflehog` |
| Telegram Bot Token | Telegram bot token from @BotFather | Empty |
| Telegram Chat ID | Channel/chat ID for notifications | Empty |
| Auto-scan JavaScript URLs | Automatically scan detected JS files | Enabled |
| Send Findings to Telegram | Send findings to Telegram | Enabled |

## Usage

1. **Start Monitoring**: The extension automatically monitors HTTP traffic when enabled
2. **Browse Websites**: Navigate to websites with JavaScript files
3. **View Results**: Scan results appear in the JSHunter interface
4. **Review Findings**: Click on findings to see details
5. **Telegram Notifications**: Verified and unverified secrets are sent to Telegram with emojis

## Troubleshooting

### Extension Not Loading
- **Check File Path**: Ensure the path to `jshunter_extension.py` is correct
- **Python Type**: Make sure you selected "Python" as the extension type
- **File Permissions**: Ensure Burp Suite can read the file
- **Error Logs**: Check the "Errors" tab in Extensions for error messages

### TruffleHog Not Found
- **Verify Installation**: Run `trufflehog --version` in terminal
- **Check Path**: Ensure the path in settings is correct
- **Test Button**: Use the "Test TruffleHog" button to verify
- **Permissions**: Ensure TruffleHog binary is executable

### Telegram Not Working
- **Verify Token**: Check that the bot token is correct
- **Verify Chat ID**: Ensure the chat ID is correct (may be negative for channels)
- **Test Button**: Use the "Test Telegram" button to verify connection
- **Bot Permissions**: Ensure the bot is added as administrator to your channel
- **API Access**: Verify you can access `https://api.telegram.org/bot<TOKEN>/getMe`

### No JavaScript URLs Detected
- **Auto-scan Enabled**: Check that auto-scanning is enabled in settings
- **HTTP Traffic**: Ensure you're browsing websites with JavaScript files
- **File Extensions**: Look for `.js` files in HTTP traffic
- **Proxy Settings**: Verify Burp Suite proxy is configured correctly

### Performance Issues
- **Large Files**: Very large JavaScript files may take time to scan
- **Multiple Scans**: Avoid scanning the same URL multiple times
- **TruffleHog Timeout**: The extension has a 60-second timeout for TruffleHog
- **Memory Usage**: Large numbers of findings may impact performance

## Advanced Configuration

### Custom TruffleHog Options
The extension uses the following TruffleHog command:
```bash
trufflehog filesystem "/path/to/file" --json
```

### Telegram Message Format
The extension sends formatted messages to Telegram:
- **Verified Secrets**: Marked with 🔴 `[VERIFIED]` and red circle emoji
- **Unverified Secrets**: Marked with 🟡 `[UNVERIFIED]` and yellow circle emoji
- **Markdown Formatting**: Uses Telegram Markdown for rich text
- **Line Numbers**: Shows the line where the secret was found
- **Code Blocks**: Secrets are displayed in code blocks for easy copying

### File Cleanup
- Temporary JavaScript files are automatically deleted after scanning
- Cleanup runs on extension startup and when clicking "Cleanup Temp Files"
- Files are stored in the system's temporary directory

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/jshunter-burp/issues)
- **Documentation**: [Burp Suite Extensions](https://portswigger.net/burp/documentation/desktop/extensions)
- **TruffleHog**: [TruffleHog Documentation](https://docs.trufflesecurity.com/)

## Uninstallation

1. **Open Burp Suite**
2. **Go to Extensions** → **Extensions**
3. **Find JSHunter**: Look for the JSHunter extension in the list
4. **Remove Extension**: Click **Remove** button
5. **Restart Burp Suite**: Restart to complete removal
