# macOS Development Environment Setup

An automated setup script for macOS development environments with JSON configuration support, progress tracking, and native notifications.

## Features

- **Automated Installation**: Complete hands-free setup of your development environment
- **JSON Configuration**: Customize everything via `setup_config.json`
- **Multiple Output Modes**: Minimal, normal, or verbose output
- **Native Notifications**: macOS notification center integration
- **Comprehensive Logging**: Detailed logs saved to `~/macos_setup_logs/`
- **Architecture Detection**: Automatic Apple Silicon/Intel detection
- **Idempotent**: Safe to run multiple times - skips already installed items

## Installation

```bash
# Download files
curl -O https://raw.githubusercontent.com/taslabs-net/macos-setup/main/setup.py
curl -o setup_config.json https://raw.githubusercontent.com/taslabs-net/macos-setup/main/setup_config.example.json

# Edit with your information
nano setup_config.json
```

## Quick Start

### Basic Usage

```bash
# Run with default interactive mode
python3 setup.py

# Run with JSON configuration (recommended)
python3 setup.py -c setup_config.json

# Dry run to preview changes
python3 setup.py -c setup_config.json --dry-run

# Minimal output mode
python3 setup.py -c setup_config.json -m minimal

# Verbose mode for debugging
python3 setup.py -c setup_config.json -m verbose
```

## Usage Modes

### Interactive Mode
Run without a config file and the script will prompt for:
- Your name (for Git and NPM)
- Email address (for Git and NPM)
- Author URL (for NPM)

```bash
python3 setup.py
```

### Automated Mode
Use a JSON config file for hands-free installation:

```bash
# First, copy and customize the example config
cp setup_config.example.json setup_config.json
# Edit setup_config.json with your details

# Run with config
python3 setup.py -c setup_config.json
```

## Configuration

Edit `setup_config.json` to customize your setup:

```json
{
  "user": {
    "name": "Your Name",
    "email": "your.email@example.com",
    "author_url": "yourwebsite.com"
  },
  "output": {
    "mode": "normal",
    "show_time_remaining": true
  },
  "notifications": {
    "enabled": true,
    "on_complete": true,
    "on_error": true
  },
  "packages": {
    "gui_apps": {
      "apps": ["firefox", "docker", "slack"]
    },
    "cli_tools": {
      "tools": ["git", "nvm", "ripgrep"]
    }
  }
}
```

## What Gets Installed

### System Configuration
- macOS preferences (screenshots format, hidden files, Finder settings)
- SSH keys for GitHub
- Git configuration with your details

### Development Tools
- **Homebrew**: Package manager for macOS
- **Rust**: Systems programming language with cargo tools
- **Node.js**: Via NVM with npm configuration
- **Python**: pyenv and pipx support
- **Shell**: Oh My Zsh with plugins, Starship prompt

### Applications (Configurable)
- **Browsers**: Chrome, Firefox, Brave
- **Development**: iTerm2, Cursor, Claude Code, OrbStack
- **Productivity**: Obsidian, Raycast
- **Communication**: Slack, Discord
- **Design**: Figma
- **Utilities**: ngrok, ImageOptim

### CLI Tools (Configurable)
- git, nvm, yarn, pnpm
- wget, cmake, ffmpeg, make, tree
- ripgrep, fzf, bat, exa, htop
- jq, tldr, gh (GitHub CLI)

## Output Modes

### Minimal Mode (`-m minimal`)
- Shows only essential information
- Perfect for automated/CI environments
- Displays: package names and final status

### Normal Mode (default)
- Balanced output with progress indicators
- Shows elapsed time and remaining estimates
- Displays installation status for each package

### Verbose Mode (`-m verbose`)
- Detailed output for debugging
- Shows command outputs
- Includes all logging information

## Logging

Logs are automatically saved to `~/macos_setup_logs/`:
- `setup_TIMESTAMP.log` - Main installation log
- `setup_detail_TIMESTAMP.log` - Detailed command outputs

## System Requirements

- macOS 10.15 or later
- Administrator access (for some installations)
- Internet connection
- Python 3.6+

## Architecture Support

The script automatically detects and configures for:
- **Apple Silicon (M1/M2/M3)**: Uses `/opt/homebrew`
- **Intel**: Uses `/usr/local`

## Customization

### Adding Packages

Edit `setup_config.json`:

```json
"gui_apps": {
  "apps": [
    "existing-app",
    "your-new-app"
  ]
}
```

### Changing Time Estimates

Adjust in `setup_config.json`:

```json
"time_estimates": {
  "gui_app": 30,
  "cli_tool": 10,
  "rust_install": 120
}
```

### Disabling Notifications

```bash
python3 applescript_enhanced.py -c setup_config.json --no-notifications
```

Or in config:

```json
"notifications": {
  "enabled": false
}
```

## Safety Features

- **Dry Run Mode**: Preview changes without making them
- **Backup Creation**: Automatically backs up existing configurations
- **Skip Existing**: Won't reinstall already-present packages
- **Error Recovery**: Continues installation even if individual packages fail
- **Comprehensive Logging**: Full audit trail of all actions

## Troubleshooting

### Common Issues

1. **Permission Denied**
   - Some installations may require sudo access
   - Terminal needs Full Disk Access in System Preferences

2. **Package Already Installed**
   - Script safely skips existing packages
   - Check logs for details

3. **Network Issues**
   - Script will retry failed downloads (configurable)
   - Check internet connection

### Debug Mode

Run with verbose output:
```bash
python3 applescript_enhanced.py -c setup_config.json -m verbose
```

Check logs:
```bash
ls -la ~/macos_setup_logs/
tail -f ~/macos_setup_logs/setup_*.log
```

## Author

Created by Timothy Schneider (tim@taslabs.net)
