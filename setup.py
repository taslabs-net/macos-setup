#!/usr/bin/env python3
"""
Enhanced macOS Setup Script with Config File Support
Automates the installation and configuration of a development environment on macOS
"""

import subprocess
import os
import sys
import time
import logging
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Only JSON configuration is supported

# Output Modes
class OutputMode(Enum):
    MINIMAL = "minimal"
    NORMAL = "normal"
    VERBOSE = "verbose"

# Global configuration
@dataclass
class Config:
    """Global configuration from file or defaults"""
    user_name: str = ""
    user_email: str = ""
    author_url: str = ""
    output_mode: OutputMode = OutputMode.NORMAL
    notifications_enabled: bool = True
    show_time_remaining: bool = True
    config_data: Dict = None

    def __post_init__(self):
        if self.config_data is None:
            self.config_data = {}

# Setup logging
def setup_logging(output_mode: OutputMode = OutputMode.NORMAL, log_level: str = "INFO"):
    """Configure logging based on output mode"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = Path.home() / "macos_setup_logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"setup_{timestamp}.log"

    # Create main logger
    logger = logging.getLogger('main')
    logger.setLevel(getattr(logging, log_level.upper()))

    # File handler - always detailed
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

    # Console handler based on output mode
    console_handler = logging.StreamHandler()
    if output_mode == OutputMode.MINIMAL:
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(logging.Formatter('%(message)s'))
    elif output_mode == OutputMode.VERBOSE:
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    else:  # NORMAL
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter('%(message)s'))

    logger.addHandler(console_handler)

    # Detail logger for commands
    detail_logger = logging.getLogger('detail')
    detail_logger.setLevel(logging.DEBUG)
    detail_handler = logging.FileHandler(log_dir / f"setup_detail_{timestamp}.log")
    detail_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    detail_logger.addHandler(detail_handler)

    return log_file, logger, detail_logger

# Time estimation
class TimeEstimator:
    """Estimate and track installation time"""
    def __init__(self, config: Dict = None):
        self.estimates = {
            'gui_app': 30,
            'cli_tool': 10,
            'rust_install': 120,
            'node_install': 60,
            'oh_my_zsh': 30,
            'configuration': 5
        }

        # Override with config values if provided
        if config and 'time_estimates' in config:
            self.estimates.update(config['time_estimates'])

        self.start_time = datetime.now()
        self.completed_tasks = []
        self.pending_tasks = []

    def estimate_total_time(self, tasks: List[tuple]) -> int:
        """Estimate total time for all tasks"""
        total = 0
        for task_name, _ in tasks:
            if 'GUI' in task_name or 'Brew Packages' in task_name:
                # Count packages if available
                total += self.estimates['gui_app'] * 10  # Rough estimate
            elif 'Rust' in task_name:
                total += self.estimates['rust_install']
            elif 'Node' in task_name:
                total += self.estimates['node_install']
            elif 'Zsh' in task_name:
                total += self.estimates['oh_my_zsh']
            else:
                total += self.estimates['configuration']
        return total

    def get_time_remaining(self, current_step: int, total_steps: int) -> str:
        """Calculate estimated time remaining"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        if current_step > 0:
            avg_time_per_step = elapsed / current_step
            remaining_steps = total_steps - current_step
            estimated_remaining = avg_time_per_step * remaining_steps
            return str(timedelta(seconds=int(estimated_remaining)))
        return "Calculating..."

# macOS Notifications
class Notifier:
    """Handle macOS notifications"""
    @staticmethod
    def send(title: str, message: str, sound: bool = True):
        """Send a macOS notification"""
        try:
            script = f'''
            display notification "{message}" with title "{title}"
            '''
            if sound:
                script += ' sound name "Glass"'

            subprocess.run(['osascript', '-e', script], capture_output=True)
        except Exception as e:
            logging.debug(f"Notification failed: {e}")

# Progress Tracker with time estimation
class EnhancedProgressTracker:
    """Enhanced progress tracking with time estimation"""
    def __init__(self, config: Config, time_estimator: TimeEstimator):
        self.start_time = datetime.now()
        self.config = config
        self.time_estimator = time_estimator
        self.current_step = ""
        self.total_steps = 0
        self.completed_steps = 0
        self.logger = logging.getLogger('main')

    def start_step(self, name: str, current: int, total: int):
        self.current_step = name
        self.total_steps = total
        self.completed_steps = current - 1
        elapsed = str(datetime.now() - self.start_time).split('.')[0]

        if self.config.output_mode != OutputMode.MINIMAL:
            print(f"\n{'='*60}")
            print(f"Progress: Step {current}/{total} ({int(current/total*100)}%)")
            print(f"Elapsed: {elapsed}")

            if self.config.show_time_remaining:
                remaining = self.time_estimator.get_time_remaining(current - 1, total)
                print(f"Estimated remaining: {remaining}")

            print(f"Current: {name}")
            print(f"{'='*60}")

        self.logger.info(f"Starting Step {current}/{total}: {name}")

    def update_progress(self, message: str):
        if self.config.output_mode == OutputMode.VERBOSE:
            print(f"  > {message}")
        elif self.config.output_mode == OutputMode.NORMAL:
            print(f"  > {message}")
        # Minimal mode shows nothing

        self.logger.info(f"  {message}")

    def complete_step(self):
        self.completed_steps += 1
        if self.config.output_mode != OutputMode.MINIMAL:
            print(f"  [COMPLETE] {self.current_step}")
        self.logger.info(f"Completed: {self.current_step}")

# Load configuration from file
def load_config(config_file: Optional[Path]) -> Dict:
    """Load configuration from JSON file"""
    if not config_file or not config_file.exists():
        return {}

    content = config_file.read_text()

    if config_file.suffix == '.json':
        return json.loads(content)
    else:
        raise ValueError(f"Only JSON config files are supported. Got: {config_file.suffix}")

# Load configuration
def load_user_config(config_data: Dict) -> Config:
    """Load user configuration from config file"""
    config = Config()

    # Load user config from file
    if 'user' in config_data:
        user_data = config_data['user']
        config.user_name = user_data.get('name', '')
        config.user_email = user_data.get('email', '')
        config.author_url = user_data.get('author_url', '')
    else:
        print("[ERROR] User configuration not found in config file.")
        print("Please ensure your config file contains a 'user' section with name and email.")
        sys.exit(1)

    # Set output mode from config
    if 'output' in config_data:
        mode = config_data['output'].get('mode', 'normal')
        config.output_mode = OutputMode(mode)
        config.show_time_remaining = config_data['output'].get('show_time_remaining', True)

    # Set notification preferences
    if 'notifications' in config_data:
        config.notifications_enabled = config_data['notifications'].get('enabled', True)

    config.config_data = config_data
    return config

# Command execution with proper logging
def run_command(cmd, shell=False, check=True, show_output=False, verbose=False, timeout=300):
    """Execute a shell command with appropriate logging and timeout"""
    detail_logger = logging.getLogger('detail')

    cmd_str = cmd if isinstance(cmd, str) else ' '.join(cmd)
    detail_logger.debug(f"Executing: {cmd_str}")

    try:
        if show_output or verbose:
            result = subprocess.run(cmd, shell=shell, check=check, timeout=timeout)
            return result
        else:
            result = subprocess.run(cmd, shell=shell, check=check, capture_output=True, text=True, timeout=timeout)

            if result.stdout:
                detail_logger.debug(f"STDOUT:\n{result.stdout}")
            if result.stderr:
                detail_logger.debug(f"STDERR:\n{result.stderr}")

            return result
    except subprocess.TimeoutExpired as e:
        detail_logger.error(f"Command timed out after {timeout}s: {cmd_str}")
        # Return a mock result object
        class MockResult:
            returncode = 1
            stdout = f"Command timed out after {timeout} seconds"
            stderr = ""
        return MockResult()
    except subprocess.CalledProcessError as e:
        detail_logger.error(f"Command failed: {str(e)}")
        # Return the actual result from the exception
        return e

# Get system information
def get_system_info():
    """Get system information and paths"""
    import platform

    system_info = {
        'arch': platform.machine(),
        'is_apple_silicon': platform.machine() == 'arm64',
        'brew_prefix': '/opt/homebrew' if platform.machine() == 'arm64' else '/usr/local',
        'home': str(Path.home())
    }

    if not Path(system_info['brew_prefix']).exists():
        if Path('/opt/homebrew').exists():
            system_info['brew_prefix'] = '/opt/homebrew'
        elif Path('/usr/local').exists():
            system_info['brew_prefix'] = '/usr/local'

    return system_info

# Installation functions
def configure_macos(config: Config):
    """Configure macOS system preferences based on config"""
    settings = config.config_data.get('macos', {}).get('settings', {})

    if not config.config_data.get('macos', {}).get('configure', True):
        config.logger.info("Skipping macOS configuration (disabled in config)")
        return

    print("Configuring macOS preferences...")
    library_path = str(Path.home() / "Library")

    commands = []

    if settings.get('screenshots_format'):
        commands.append((f"defaults write com.apple.screencapture type {settings['screenshots_format']}",
                        f"Set screenshots to {settings['screenshots_format'].upper()} format"))

    if settings.get('show_hidden_files', True):
        commands.append(("defaults write com.apple.finder AppleShowAllFiles YES", "Show hidden files"))

    if settings.get('show_library_folder', True):
        commands.append((f"chflags nohidden {library_path}", "Show Library folder"))

    if settings.get('finder_path_bar', True):
        commands.append(("defaults write com.apple.finder ShowPathbar -bool true", "Show path bar in Finder"))

    if settings.get('finder_status_bar', True):
        commands.append(("defaults write com.apple.finder ShowStatusBar -bool true", "Show status bar in Finder"))

    # Claude configuration
    commands.append(("claude config set -g autoUpdates false", "Disable Claude auto-updates"))

    for cmd, desc in commands:
        if config.output_mode != OutputMode.MINIMAL:
            print(f"  -> {desc}")
        run_command(cmd, shell=True, verbose=(config.output_mode == OutputMode.VERBOSE))

    if commands:
        run_command("killall Finder", shell=True)

def configure_git(config: Config):
    """Configure Git based on config"""
    git_config = config.config_data.get('git', {})
    
    if not git_config.get('configure', True):
        print("Skipping Git configuration (disabled in config)")
        return
    
    print("Configuring Git...")
    
    # Set user information
    if config.user_name:
        run_command(["git", "config", "--global", "user.name", config.user_name])
        print(f"  -> Set user.name to '{config.user_name}'")
    
    if config.user_email:
        run_command(["git", "config", "--global", "user.email", config.user_email])
        print(f"  -> Set user.email to '{config.user_email}'")
    
    # Set default branch
    default_branch = git_config.get('default_branch', 'main')
    run_command(["git", "config", "--global", "init.defaultBranch", default_branch])
    print(f"  -> Set default branch to '{default_branch}'")
    
    # Configure aliases
    aliases_config = git_config.get('aliases', {})
    if aliases_config.get('enabled', True):
        custom_aliases = aliases_config.get('custom', {})
        for alias, command in custom_aliases.items():
            run_command(["git", "config", "--global", f"alias.{alias}", command])
            print(f"  -> Set alias '{alias}' to '{command}'")

def install_homebrew(config: Config):
    """Install or update Homebrew"""
    homebrew_config = config.config_data.get('packages', {}).get('homebrew', {})
    
    if not homebrew_config.get('install', True):
        print("Skipping Homebrew installation (disabled in config)")
        return
    
    # Check if Homebrew is already installed
    brew_path = '/opt/homebrew/bin/brew' if os.uname().machine == 'arm64' else '/usr/local/bin/brew'
    
    if os.path.exists(brew_path):
        print("Homebrew already installed")
        if homebrew_config.get('update', True):
            print("Updating Homebrew...")
            run_command([brew_path, "update"], show_output=True)
    else:
        print("Installing Homebrew...")
        install_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        run_command(install_cmd, shell=True, show_output=True)
        
        # Add Homebrew to PATH for this session
        if os.uname().machine == 'arm64':
            os.environ['PATH'] = f"/opt/homebrew/bin:{os.environ.get('PATH', '')}"
        else:
            os.environ['PATH'] = f"/usr/local/bin:{os.environ.get('PATH', '')}"

def generate_ssh_key(config: Config):
    """Generate SSH key for GitHub"""
    ssh_config = config.config_data.get('ssh', {})
    
    if not ssh_config.get('generate_key', True):
        print("Skipping SSH key generation (disabled in config)")
        return
    
    print("Setting up SSH key for GitHub...")
    
    key_type = ssh_config.get('key_type', 'ed25519')
    key_name = ssh_config.get('key_name', 'github')
    ssh_dir = Path.home() / '.ssh'
    key_path = ssh_dir / f"id_{key_type}_{key_name}"
    
    # Create .ssh directory if it doesn't exist
    ssh_dir.mkdir(mode=0o700, exist_ok=True)
    
    if key_path.exists():
        print(f"  -> SSH key already exists: {key_path}")
    else:
        print(f"  -> Generating {key_type} SSH key: {key_path}")
        cmd = [
            'ssh-keygen', '-t', key_type,
            '-f', str(key_path),
            '-C', config.user_email or 'user@example.com',
            '-N', ''  # No passphrase
        ]
        run_command(cmd)
    
    # Add to keychain if on macOS
    if ssh_config.get('add_to_keychain', True):
        print("  -> Adding SSH key to keychain")
        # Update SSH config
        ssh_config_file = ssh_dir / 'config'
        config_content = f"""
Host github.com
    AddKeysToAgent yes
    UseKeychain yes
    IdentityFile {key_path}
"""
        
        if ssh_config_file.exists():
            existing_content = ssh_config_file.read_text()
            if 'Host github.com' not in existing_content:
                ssh_config_file.write_text(existing_content + config_content)
        else:
            ssh_config_file.write_text(config_content)
            ssh_config_file.chmod(0o600)
        
        # Add key to ssh-agent and keychain
        run_command(['ssh-add', '--apple-use-keychain', str(key_path)])
    
    # Display public key
    pub_key_path = f"{key_path}.pub"
    if os.path.exists(pub_key_path):
        with open(pub_key_path, 'r') as f:
            pub_key = f.read().strip()
        print(f"\n  -> Public key for GitHub:")
        print(f"     {pub_key}")
        print(f"\n  -> Add this key to GitHub at: https://github.com/settings/keys")

def install_rust(config: Config):
    """Install Rust and cargo tools"""
    rust_config = config.config_data.get('development', {}).get('rust', {})
    
    if not rust_config.get('install', True):
        print("Skipping Rust installation (disabled in config)")
        return
    
    print("Installing Rust...")
    
    # First ensure rustup is installed via Homebrew
    result = run_command(["brew", "list", "rustup"], check=False)
    if result.returncode != 0:
        print("  -> Installing rustup via Homebrew")
        run_command(["brew", "install", "rustup"], show_output=True)
    
    # Check if Rust toolchain is installed
    rustc_path = Path.home() / '.cargo' / 'bin' / 'rustc'
    cargo_path = Path.home() / '.cargo' / 'bin' / 'cargo'
    
    if rustc_path.exists():
        print("  -> Rust toolchain already installed")
        # Use full path to avoid PATH issues
        result = run_command([str(rustc_path), '--version'], check=False)
        if result.returncode == 0:
            print(f"     {result.stdout.strip()}")
    else:
        print("  -> Installing Rust toolchain via rustup")
        run_command(["rustup-init", "-y"], show_output=True, timeout=600)
        
        # Add cargo to PATH for this session
        cargo_bin = str(Path.home() / '.cargo' / 'bin')
        os.environ['PATH'] = f"{cargo_bin}:{os.environ.get('PATH', '')}"

    # Install rustup components
    rustup_path = Path.home() / '.cargo' / 'bin' / 'rustup'
    if rustup_path.exists():
        print("  -> Installing rustup components (clippy, rustfmt)")
        run_command([str(rustup_path), 'component', 'add', 'clippy', 'rustfmt'],
                   check=False, show_output=False)

    # Install cargo tools
    cargo_tools = rust_config.get('cargo_tools', [])
    if cargo_tools and cargo_path.exists():
        for tool in cargo_tools:
            print(f"  -> Installing cargo tool: {tool}")
            # Check if tool is already installed
            check_cmd = [str(cargo_path), 'install', '--list']
            result = run_command(check_cmd, check=False)
            if result.returncode == 0 and tool in result.stdout:
                print(f"     {tool} already installed")
            else:
                # Use --force to ensure installation even if partially installed
                install_result = run_command([str(cargo_path), 'install', '--force', tool],
                                           check=False, show_output=False, timeout=300)
                if install_result.returncode != 0:
                    print(f"     Warning: Failed to install {tool}, trying without --force")
                    run_command([str(cargo_path), 'install', tool],
                              check=False, show_output=False, timeout=300)

def install_node(config: Config):
    """Install Node.js via NVM"""
    node_config = config.config_data.get('development', {}).get('node', {})
    
    if not node_config.get('install', True):
        print("Skipping Node.js installation (disabled in config)")
        return
    
    print("Installing Node.js via NVM...")
    
    # Ensure NVM is installed via Homebrew
    result = run_command(["brew", "list", "nvm"], check=False)
    if result.returncode != 0:
        print("  -> Installing NVM via Homebrew")
        run_command(["brew", "install", "nvm"], show_output=True)
        
        # Create .nvm directory
        nvm_dir = Path.home() / '.nvm'
        nvm_dir.mkdir(exist_ok=True)
    
    # Install Node version
    node_version = node_config.get('version', 'lts')
    
    # Handle 'lts' keyword properly
    if node_version.lower() == 'lts':
        node_version = '--lts'
    
    print(f"  -> Installing Node.js {node_version}")
    
    # Source NVM and install Node
    nvm_cmd = f"""
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
    nvm install {node_version}
    nvm use {node_version}
    nvm alias default {node_version}
    """
    run_command(nvm_cmd, shell=True, show_output=True)
    
    # Link node if installed via Homebrew (for compatibility)
    print("  -> Ensuring node is properly linked")
    run_command(["brew", "link", "node"], check=False, show_output=False)

    # Install npm packages
    npm_packages = node_config.get('npm_packages', [])
    if npm_packages:
        npm_cmd_base = f"""
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
        """
        for package in npm_packages:
            print(f"  -> Installing npm package: {package}")
            npm_cmd = npm_cmd_base + f"npm install -g {package}"
            run_command(npm_cmd, shell=True, show_output=False)

def install_oh_my_zsh(config: Config):
    """Install Oh My Zsh and plugins"""
    omz_config = config.config_data.get('shell', {}).get('oh_my_zsh', {})
    
    if not omz_config.get('install', True):
        print("Skipping Oh My Zsh installation (disabled in config)")
        return
    
    print("Installing Oh My Zsh...")
    
    omz_dir = Path.home() / '.oh-my-zsh'
    
    if omz_dir.exists():
        print("  -> Oh My Zsh already installed")
    else:
        print("  -> Installing Oh My Zsh")
        install_cmd = 'sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended'
        run_command(install_cmd, shell=True, show_output=True)
    
    # Install plugins
    plugins = omz_config.get('plugins', [])
    if plugins:
        custom_plugins_dir = omz_dir / 'custom' / 'plugins'
        custom_plugins_dir.mkdir(parents=True, exist_ok=True)
        
        # Install custom plugins that aren't bundled
        plugin_repos = {
            'zsh-autosuggestions': 'https://github.com/zsh-users/zsh-autosuggestions',
            'zsh-syntax-highlighting': 'https://github.com/zsh-users/zsh-syntax-highlighting',
            'zsh-completions': 'https://github.com/zsh-users/zsh-completions'
        }
        
        for plugin in plugins:
            if plugin in plugin_repos:
                plugin_dir = custom_plugins_dir / plugin
                if not plugin_dir.exists():
                    print(f"  -> Installing plugin: {plugin}")
                    run_command(['git', 'clone', plugin_repos[plugin], str(plugin_dir)])
        
        # Update .zshrc to include plugins
        zshrc_path = Path.home() / '.zshrc'
        if zshrc_path.exists():
            zshrc_content = zshrc_path.read_text()
            plugins_line = f"plugins=({' '.join(plugins)})"
            
            # Replace existing plugins line
            import re
            new_content = re.sub(r'^plugins=\([^)]*\)', plugins_line, zshrc_content, flags=re.MULTILINE)
            if new_content != zshrc_content:
                zshrc_path.write_text(new_content)
                print(f"  -> Updated .zshrc with plugins: {', '.join(plugins)}")

def install_starship(config: Config):
    """Install and configure Starship prompt"""
    starship_config = config.config_data.get('shell', {}).get('starship', {})
    
    if not starship_config.get('install', True):
        print("Skipping Starship installation (disabled in config)")
        return
    
    print("Installing Starship prompt...")
    
    # Install Starship via Homebrew
    result = run_command(["brew", "list", "starship"], check=False)
    if result.returncode == 0:
        print("  -> Starship already installed via Homebrew")
    else:
        print("  -> Installing Starship via Homebrew")
        run_command(["brew", "install", "starship"], show_output=True)
    
    # Configure Starship in shell
    if starship_config.get('configure', True):
        zshrc_path = Path.home() / '.zshrc'
        if zshrc_path.exists():
            zshrc_content = zshrc_path.read_text()
            starship_init = 'eval "$(starship init zsh)"'
            
            if starship_init not in zshrc_content:
                print("  -> Adding Starship to .zshrc")
                with open(zshrc_path, 'a') as f:
                    f.write(f"\n# Starship prompt\n{starship_init}\n")
        
        # Create basic Starship config
        starship_config_dir = Path.home() / '.config'
        starship_config_dir.mkdir(exist_ok=True)
        starship_toml = starship_config_dir / 'starship.toml'
        
        if not starship_toml.exists():
            print("  -> Creating Starship configuration")
            basic_config = """# Starship configuration
[character]
success_symbol = "[➜](bold green)"
error_symbol = "[✗](bold red)"

[directory]
truncation_length = 3
truncate_to_repo = true
"""
            starship_toml.write_text(basic_config)

def configure_shell_paths(config: Config):
    """Configure shell PATH settings for installed tools"""
    print("Configuring shell PATH settings...")

    shell_rc = Path.home() / '.zshrc'
    if not shell_rc.exists():
        shell_rc = Path.home() / '.bash_profile'

    if not shell_rc.exists():
        print("  -> No shell configuration file found, skipping PATH setup")
        return

    # Read existing content
    shell_content = shell_rc.read_text()
    additions = []

    # 1. Homebrew shellenv (if not already present)
    if 'brew shellenv' not in shell_content:
        if os.uname().machine == 'arm64':
            brew_prefix = '/opt/homebrew'
        else:
            brew_prefix = '/usr/local'

        if Path(f'{brew_prefix}/bin/brew').exists():
            print("  -> Adding Homebrew to PATH")
            additions.append(f'\n# Homebrew\neval "$({brew_prefix}/bin/brew shellenv)"')

    # 2. Cargo/Rust PATH (if not already present)
    cargo_bin = Path.home() / '.cargo' / 'bin'
    if cargo_bin.exists() and '.cargo/bin' not in shell_content:
        print("  -> Adding Cargo to PATH")
        additions.append(f'\n# Rust/Cargo\nexport PATH="$HOME/.cargo/bin:$PATH"')

    # 3. Ensure NVM is properly configured (update if needed)
    if (Path.home() / '.nvm').exists():
        if 'NVM_DIR' not in shell_content:
            print("  -> Adding NVM configuration")
            if os.uname().machine == 'arm64':
                nvm_source = '/opt/homebrew/opt/nvm'
            else:
                nvm_source = '/usr/local/opt/nvm'

            nvm_config = f'''
# NVM (Node Version Manager)
export NVM_DIR="$HOME/.nvm"
[ -s "{nvm_source}/nvm.sh" ] && . "{nvm_source}/nvm.sh"
[ -s "{nvm_source}/etc/bash_completion.d/nvm" ] && . "{nvm_source}/etc/bash_completion.d/nvm"'''
            additions.append(nvm_config)

    # 4. FZF shell integration (if fzf is installed but integration missing)
    if run_command(['which', 'fzf'], check=False).returncode == 0:
        fzf_shell = Path.home() / '.fzf.zsh' if 'zsh' in str(shell_rc) else Path.home() / '.fzf.bash'
        if not fzf_shell.exists() and 'fzf' not in shell_content:
            print("  -> Setting up FZF shell integration")
            if os.uname().machine == 'arm64':
                fzf_install = '/opt/homebrew/opt/fzf/install'
            else:
                fzf_install = '/usr/local/opt/fzf/install'

            if Path(fzf_install).exists():
                # Run fzf install script non-interactively
                run_command([fzf_install, '--key-bindings', '--completion', '--no-update-rc'], check=False)
                if fzf_shell.exists():
                    additions.append(f'\n# FZF\n[ -f {fzf_shell} ] && source {fzf_shell}')

    # Write additions to shell config
    if additions:
        print(f"  -> Updating {shell_rc.name}")
        with open(shell_rc, 'a') as f:
            f.write('\n' + '\n'.join(additions))
        print("  -> Shell PATH configuration complete")
    else:
        print("  -> All PATH configurations already present")

def install_brew_packages(config: Config, progress: EnhancedProgressTracker):
    """Install Homebrew packages from config"""
    packages_config = config.config_data.get('packages', {})

    # GUI Apps
    gui_apps = []
    if packages_config.get('gui_apps', {}).get('enabled', True):
        gui_apps = packages_config.get('gui_apps', {}).get('apps', [])

    # CLI Tools
    cli_tools = []
    if packages_config.get('cli_tools', {}).get('enabled', True):
        cli_tools = packages_config.get('cli_tools', {}).get('tools', [])

    total_packages = len(gui_apps) + len(cli_tools)
    current = 0

    if gui_apps:
        progress.update_progress(f"Installing {len(gui_apps)} GUI applications...")
        for app in gui_apps:
            current += 1
            if config.output_mode == OutputMode.MINIMAL:
                print(f"[{current}/{total_packages}] {app}")
            else:
                print(f"\n{'='*20} [{current}/{total_packages}] {'='*20}")
                print(f"Installing GUI app: {app}")
                print(f"{'='*50}")

            # Check if already installed via Homebrew
            result = run_command(["brew", "list", "--cask", app], check=False)
            is_brew_installed = (result.returncode == 0)
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"  > [{timestamp}] Starting installation of {app}...")
            if is_brew_installed:
                # Already managed by Homebrew, install normally
                print(f"  > [{timestamp}] {app} already managed by Homebrew, updating if needed...")
                result = run_command(["brew", "install", "--cask", app], check=False,
                                        show_output=True, verbose=(config.output_mode == OutputMode.VERBOSE),
                                        timeout=600)  # 10 minutes for large apps
            else:
                # Not managed by Homebrew (or not installed), force install to ensure Homebrew management
                print(f"  > [{timestamp}] {app} not managed by Homebrew, force installing...")
                result = run_command(["brew", "install", "--cask", "--force", app], check=False,
                                        show_output=True, verbose=(config.output_mode == OutputMode.VERBOSE),
                                        timeout=600)  # 10 minutes for large apps
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"  > [{timestamp}] Finished processing {app}")

            if config.output_mode != OutputMode.MINIMAL:
                if result.returncode == 0:
                    print(f"[OK] {app} installed successfully")
                else:
                    print(f"[WARN] {app} may already be installed or failed")
                print(f"Progress: {current}/{total_packages} packages completed")

    if cli_tools:
        progress.update_progress(f"Installing {len(cli_tools)} CLI tools...")
        for tool in cli_tools:
            current += 1
            if config.output_mode == OutputMode.MINIMAL:
                print(f"[{current}/{total_packages}] {tool}")
            else:
                print(f"\n  [{current}/{total_packages}] Installing {tool}...")

            # Check if already installed via Homebrew
            result = run_command(["brew", "list", tool], check=False)
            is_brew_installed = (result.returncode == 0)
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"  > [{timestamp}] Starting installation of {tool}...")
            if is_brew_installed:
                # Already managed by Homebrew, install normally
                print(f"  > [{timestamp}] {tool} already managed by Homebrew, updating if needed...")
                result = run_command(["brew", "install", tool], check=False,
                                        show_output=True, verbose=(config.output_mode == OutputMode.VERBOSE),
                                        timeout=300)  # 5 minutes for CLI tools
            else:
                # Not managed by Homebrew (or not installed), force install to ensure Homebrew management
                print(f"  > [{timestamp}] {tool} not managed by Homebrew, force installing...")
                result = run_command(["brew", "install", "--force", tool], check=False,
                                        show_output=True, verbose=(config.output_mode == OutputMode.VERBOSE),
                                        timeout=300)  # 5 minutes for CLI tools
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"  > [{timestamp}] Finished processing {tool}")

            if config.output_mode != OutputMode.MINIMAL:
                if result.returncode == 0:
                    print(f"     [OK] {tool} installed")
                    # Link tools if needed
                    if tool in ['yarn', 'pnpm']:
                        link_result = run_command(["brew", "link", "--overwrite", tool], check=False)
                        if link_result.returncode == 0:
                            print(f"     [OK] {tool} linked")
                else:
                    print(f"     [WARN] {tool} may already be installed or failed")

def main():
    """Main setup function with config file support"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Enhanced macOS Development Environment Setup')
    parser.add_argument('-c', '--config', type=Path, required=True, 
                       help='Configuration file (JSON) - Required')
    parser.add_argument('-m', '--mode', choices=['minimal', 'normal', 'verbose'],
                       default='normal', help='Output mode')
    parser.add_argument('--no-notifications', action='store_true',
                       help='Disable notifications')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be installed without installing')

    args = parser.parse_args()

    # Load configuration
    if not args.config.exists():
        print(f"[ERROR] Configuration file not found: {args.config}")
        print("\nPlease create a configuration file first:")
        print("  cp setup_config.example.json setup_config.json")
        print("  Then edit setup_config.json with your information")
        sys.exit(1)
    
    print(f"Loading configuration from: {args.config}")
    config_data = load_config(args.config)

    # Get user configuration
    config = load_user_config(config_data)

    # Override with command line arguments
    if args.mode:
        config.output_mode = OutputMode(args.mode)
    if args.no_notifications:
        config.notifications_enabled = False

    # Setup logging
    log_level = config.config_data.get('output', {}).get('log_level', 'INFO')
    log_file, logger, detail_logger = setup_logging(config.output_mode, log_level)
    config.logger = logger

    # Log startup
    logger.info("=" * 60)
    logger.info("Enhanced macOS Setup Script Started")
    logger.info(f"Configuration file: {args.config if args.config else 'None'}")
    logger.info(f"Output mode: {config.output_mode.value}")
    logger.info(f"User: {config.user_name} <{config.user_email}>")
    logger.info("=" * 60)

    # System info
    system_info = get_system_info()

    # Initialize time estimator and progress tracker
    time_estimator = TimeEstimator(config.config_data)
    progress = EnhancedProgressTracker(config, time_estimator)

    # Define installation steps
    steps = []

    if config.config_data.get('macos', {}).get('configure', True):
        steps.append(("Configure macOS", lambda: configure_macos(config)))

    if config.config_data.get('packages', {}).get('homebrew', {}).get('install', True):
        steps.append(("Install/Update Homebrew", lambda: install_homebrew(config)))

    if config.config_data.get('ssh', {}).get('generate_key', True):
        steps.append(("Generate SSH Key", lambda: generate_ssh_key(config)))

    if config.config_data.get('git', {}).get('configure', True):
        steps.append(("Configure Git", lambda: configure_git(config)))

    if config.config_data.get('development', {}).get('rust', {}).get('install', True):
        steps.append(("Install Rust", lambda: install_rust(config)))

    if config.config_data.get('development', {}).get('node', {}).get('install', True):
        steps.append(("Install Node.js", lambda: install_node(config)))

    if config.config_data.get('shell', {}).get('oh_my_zsh', {}).get('install', True):
        steps.append(("Install Oh My Zsh", lambda: install_oh_my_zsh(config)))

    if config.config_data.get('shell', {}).get('starship', {}).get('install', True):
        steps.append(("Install Starship", lambda: install_starship(config)))

    if config.config_data.get('packages', {}):
        steps.append(("Install Brew Packages", lambda: install_brew_packages(config, progress)))

    # Add shell PATH configuration as the last step
    steps.append(("Configure Shell PATHs", lambda: configure_shell_paths(config)))

    # Send start notification
    if config.notifications_enabled:
        Notifier.send("macOS Setup", "Starting development environment setup...")

    # Show what will be installed
    if config.output_mode != OutputMode.MINIMAL:
        print("\n" + "=" * 60)
        print("Starting macOS Development Environment Setup")
        print("=" * 60)
        print(f"\nLog files: {log_file.parent}")
        print(f"Output mode: {config.output_mode.value}")

        if config.show_time_remaining:
            total_time = time_estimator.estimate_total_time(steps)
            print(f"Estimated time: {str(timedelta(seconds=total_time))}")

        print("\nSteps to execute:")
        for i, (name, _) in enumerate(steps, 1):
            print(f"  {i}. {name}")
        
        if not args.dry_run:
            print("\nStarting installation...")
            time.sleep(2)  # Brief pause to let user see what will be installed

    # Dry run mode
    if args.dry_run:
        print("\n[DRY RUN] Would execute the following steps:")
        for i, (name, _) in enumerate(steps, 1):
            print(f"  {i}. {name}")
        print("\n[DRY RUN] No changes were made.")
        return

    # Execute steps
    failed_steps = []
    successful_steps = []

    for i, (name, func) in enumerate(steps, 1):
        progress.start_step(name, i, len(steps))

        try:
            func()
            successful_steps.append(name)
            progress.complete_step()
        except Exception as e:
            logger.error(f"Step failed: {name} - {e}")
            failed_steps.append((name, str(e)))

            if config.notifications_enabled and config.config_data.get('notifications', {}).get('on_error', True):
                Notifier.send("Setup Error", f"Failed: {name}")

    # Summary
    elapsed = str(datetime.now() - progress.start_time).split('.')[0]

    if config.output_mode != OutputMode.MINIMAL:
        print("\n" + "=" * 60)
        print("SETUP COMPLETE")
        print("=" * 60)
        print(f"Total time: {elapsed}")
        print(f"Results: {len(successful_steps)}/{len(steps)} steps succeeded")

        if successful_steps:
            print(f"\n[SUCCESS] Completed ({len(successful_steps)}):")
            for step in successful_steps:
                print(f"  - {step}")

        if failed_steps:
            print(f"\n[FAILED] ({len(failed_steps)}):")
            for step, error in failed_steps:
                print(f"  - {step}: {error[:50]}...")
    else:
        # Minimal output
        print(f"\nCompleted: {len(successful_steps)}/{len(steps)} steps in {elapsed}")

    # Send completion notification
    if config.notifications_enabled and config.config_data.get('notifications', {}).get('on_complete', True):
        if failed_steps:
            Notifier.send("Setup Completed with Errors",
                         f"Completed {len(successful_steps)}/{len(steps)} steps")
        else:
            Notifier.send("Setup Completed Successfully",
                         f"All {len(steps)} steps completed in {elapsed}")

    logger.info("Setup script completed")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error: {e}")
        sys.exit(1)