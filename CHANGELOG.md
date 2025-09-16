# Changelog

All notable changes to the macOS Setup project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2024-09-15

### Changed
- Consolidated to single `setup.py` script that handles both interactive and config modes
- Removed redundant `applescript.py` as enhanced version covers all functionality
- Simplified project structure

### Security
- Removed personal information from repository history
- Added `.gitignore` for personal config files
- Provided `setup_config.example.json` template

## [2.0.0] - 2024-09-15

### Added
- **Enhanced Script** (now `setup.py`)
  - JSON configuration file support
  - Time estimation with real-time updates
  - Multiple output modes (minimal, normal, verbose)
  - macOS native notifications
  - Dry-run mode for previewing changes
  - Command-line argument parsing
  - Auto-retry for failed installations

- **Configuration System**
  - `setup_config.json` for complete customization
  - User information pre-configuration
  - Package selection control
  - Time estimate customization
  - Notification preferences
  - Installation behavior settings

- **Documentation**
  - Comprehensive README with usage examples
  - Troubleshooting guide
  - Configuration documentation

### Changed
- Moved project to organized structure in `/Users/tim/Coding/macos-setup/`
- Enhanced logging with separate detail logs
- Improved error handling and recovery

### Improved
- Better progress tracking with percentage completion
- Architecture detection (Apple Silicon vs Intel)
- Path handling for different macOS configurations
- Backup system for existing configurations

## [1.5.0] - 2024-09-15

### Added
- Comprehensive logging system
  - Main log file with high-level progress
  - Detail log with command outputs
  - Automatic log directory creation

### Changed
- Removed all emojis for cleaner, professional output
- Replaced emoji indicators with text markers ([OK], [WARN], [ERROR])
- Improved progress indicators

## [1.0.0] - 2024-09-15

### Initial Release
- **Core Features** (`applescript.py`)
  - Interactive user configuration
  - macOS system preferences configuration
  - Homebrew installation and package management
  - Development environment setup (Rust, Node.js, Python)
  - Shell configuration (Oh My Zsh, Starship)
  - SSH key generation and configuration
  - Git configuration with user details

- **Package Installation**
  - GUI applications via Homebrew Cask
  - CLI tools via Homebrew
  - Rust and cargo tools
  - Node.js via NVM
  - Python environment with pyenv

- **System Configuration**
  - macOS defaults (screenshots, Finder, hidden files)
  - Zsh configuration with plugins
  - NPM configuration with user details
  - SSH key setup for GitHub

### Features
- Progress tracking with step counter
- Automatic detection of existing installations
- Error handling with continuation
- Comprehensive installation summary
- Support for both Apple Silicon and Intel Macs

## [Unreleased]

### Planned Features
- YAML configuration support (optional)
- Package group profiles (web dev, data science, etc.)
- Backup and restore functionality
- Update checker for installed packages
- Web dashboard for monitoring
- Integration with dotfiles repositories
- Multi-user support
- Corporate proxy configuration
- Custom package repositories

### Under Consideration
- GUI interface option
- Cloud backup of configurations
- Automated testing framework
- Docker/container setup options
- Database installation options
- IDE plugin installations
- Custom shell theme configurations

## Migration Guide

### From 1.0.0 to 2.0.0

1. Move your setup to the new directory:
   ```bash
   cd /Users/tim/Coding/macos-setup/
   ```

2. Create your configuration:
   - Copy `setup_config.json`
   - Edit with your personal details
   - Customize package selections

3. Use the enhanced script:
   ```bash
   # Instead of:
   python3 applescript.py

   # Use:
   python3 applescript_enhanced.py -c setup_config.json
   ```

4. Benefits of upgrading:
   - No more interactive prompts (if configured)
   - Time estimates for installation
   - Better output control
   - Native notifications
   - Dry-run capability

## Version History

- **2.0.0** - Enhanced version with configuration support
- **1.5.0** - Professional output without emojis
- **1.0.0** - Initial interactive version

## Support

For issues or questions:
- Check the README troubleshooting section
- Review logs in `~/macos_setup_logs/`
- Create an issue in the repository