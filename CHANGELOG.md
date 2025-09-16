# Changelog

All notable changes to the macOS Setup project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-09-15

### Initial Release
- **Core Script** (`setup.py`)
  - Interactive user configuration with fallback prompts
  - JSON configuration file support via `setup_config.example.json`
  - Multiple output modes (minimal, normal, verbose)
  - macOS native notifications
  - Dry-run mode for previewing changes
  - Command-line argument parsing

- **Configuration System**
  - JSON-based configuration for complete customization
  - User information pre-configuration (name, email, author URL)
  - Package selection control for GUI apps and CLI tools
  - Notification preferences
  - macOS system settings configuration

- **System Configuration**
  - macOS defaults (screenshots format, hidden files, Finder settings)
  - Homebrew installation and package management
  - Development environment setup
  - Architecture detection (Apple Silicon vs Intel)
  - SSH key generation and Git configuration

- **Package Installation**
  - GUI applications via Homebrew Cask
  - CLI tools via Homebrew
  - Configurable package lists
  - Idempotent installation (safe to run multiple times)

### Features
- Progress tracking with step-by-step output
- Comprehensive logging system
- Error handling with continuation on failures
- Installation summary with success/failure reporting
- Support for both Apple Silicon and Intel Macs
- Clean repository structure with essential files only

## [Unreleased]

### Planned Features
- YAML configuration support (optional)
- Package group profiles (web dev, data science, etc.)
- Backup and restore functionality
- Update checker for installed packages
- Integration with dotfiles repositories

### Under Consideration
- GUI interface option
- Automated testing framework
- Custom package repositories
- IDE plugin installations

## Usage

```bash
# Download and setup
curl -O https://raw.githubusercontent.com/taslabs-net/macos-setup/main/setup.py
curl -o setup_config.json https://raw.githubusercontent.com/taslabs-net/macos-setup/main/setup_config.example.json

# Edit configuration
nano setup_config.json

# Run setup
python3 setup.py -c setup_config.json
```

## Support

For issues or questions:
- Check the README troubleshooting section
- Review logs in `~/macos_setup_logs/`
- Create an issue in the repository