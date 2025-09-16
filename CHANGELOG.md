# Changelog

All notable changes to the macOS Setup project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] - 2025-09-16

### Added
- Claude and ChatGPT to GUI apps list
- Alt-Tab window switcher to GUI apps list
- Itsycal menu bar calendar to GUI apps list
- Cloudflare Wrangler CLI tool
- GitHub CLI (gh) for repository management
- Rustup components (clippy, rustfmt) installation after Rust setup
- Node.js linking via `brew link node` for compatibility
- Force flag for cargo tools installation to handle partial installs
- Automatic PATH configuration for all installed tools (Homebrew, Cargo, NVM, FZF)

### Improved
- Cargo tools installation with fallback on failure
- Better error handling for cargo install commands
- Shell configuration now automatically adds PATH entries for installed tools
- FZF shell integration automatically configured when installed

### Documentation
- Removed redundant Usage section from README

## [1.2.0] - 2025-09-16

### Added
- Full implementation of all features (no placeholder code remaining):
  - SSH key generation with keychain integration
  - Rust installation via Homebrew rustup
  - Node.js installation via NVM with npm packages
  - Oh My Zsh installation with plugins
  - Starship prompt installation via Homebrew
- Auto-linking for yarn and pnpm after installation
- ProtonVPN to GUI apps list

### Changed
- Starship now installs via Homebrew instead of curl script
- Rust now installs via Homebrew's rustup package
- NVM properly managed through Homebrew
- Script simplified by removing interactive mode completely
- Configuration file is now required (no defaults)
- Replaced deprecated 'exa' with 'eza' CLI tool
- Node.js LTS installation properly handles version flag

### Fixed
- run_command() return value handling (tuple vs result object)
- Node.js 'lts' keyword now properly converted to '--lts' flag
- yarn and pnpm linking issues with --overwrite flag

### Removed
- Interactive mode and all related code
- Cloudflare WARP (requires sudo, not automatable)
- All placeholder implementations

## [1.1.0] - 2025-09-15

### Added
- Git configuration functionality (user name, email, aliases, default branch)
- Timeout handling for all subprocess calls (10min for GUI apps, 5min for CLI tools)
- Intelligent Homebrew management with force-install for non-Homebrew managed apps
- Timestamped progress feedback for better user experience
- Topgrade to CLI tools list

### Changed
- Removed PyYAML dependency - now JSON-only configuration
- Documentation updated to require JSON configuration (removed interactive mode)
- Enhanced visual feedback with clear status messages and progress indicators
- Improved error handling with timeout exception catching

### Fixed
- Script hanging on problematic package installations
- Incorrect script filenames in documentation

## [1.0.1] - 2025-09-15

### Added
- Joplin notes application to GUI apps list
- Visual Studio Code to GUI apps list
- CotEditor to GUI apps list
- Windsurf to GUI apps list

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
