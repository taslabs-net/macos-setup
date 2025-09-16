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

# Try to import yaml, install if necessary
try:
    import yaml
except ImportError:
    print("[INFO] PyYAML not installed. Installing...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        import yaml
        print("[OK] PyYAML installed successfully")
    except Exception as e:
        print(f"[WARNING] Could not install PyYAML: {e}")
        print("[INFO] YAML config files will not be supported. Use JSON instead.")
        yaml = None

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
    """Load configuration from YAML or JSON file"""
    if not config_file or not config_file.exists():
        return {}

    content = config_file.read_text()

    if config_file.suffix in ['.yaml', '.yml']:
        if yaml is None:
            print(f"[ERROR] YAML support not available. Please use a JSON config file instead.")
            print(f"[INFO] You can convert your YAML to JSON or install PyYAML manually:")
            print(f"       pip install pyyaml")
            sys.exit(1)
        return yaml.safe_load(content)
    elif config_file.suffix == '.json':
        return json.loads(content)
    else:
        raise ValueError(f"Unsupported config file format: {config_file.suffix}")

# Get user input or use config
def get_user_input_or_config(config_data: Dict) -> Config:
    """Get user configuration from input or config file"""
    config = Config()

    # Check if user config exists in file
    if 'user' in config_data:
        user_data = config_data['user']
        config.user_name = user_data.get('name', '')
        config.user_email = user_data.get('email', '')
        config.author_url = user_data.get('author_url', '')

    # If not in config, ask interactively
    if not config.user_name:
        print("macOS Development Environment Setup")
        print("=" * 60)
        print("Please provide your information:\n")

        while not config.user_name:
            config.user_name = input("Your Name: ").strip()
            if not config.user_name:
                print("   [!] Name cannot be empty.")

        while not config.user_email:
            config.user_email = input("Your Email: ").strip()
            if not config.user_email:
                print("   [!] Email cannot be empty.")
            elif '@' not in config.user_email:
                print("   [!] Please enter a valid email address.")
                config.user_email = ""

        config.author_url = input("Author URL (optional): ").strip()

        # Confirm
        print("\n" + "=" * 60)
        print("Configuration Summary:")
        print(f"   Name: {config.user_name}")
        print(f"   Email: {config.user_email}")
        print(f"   URL: {config.author_url or 'Not provided'}")
        print("=" * 60)

        confirm = input("\nIs this correct? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Let's try again...\n")
            return get_user_input_or_config({})

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
def run_command(cmd, shell=False, check=True, show_output=False, verbose=False):
    """Execute a shell command with appropriate logging"""
    detail_logger = logging.getLogger('detail')

    cmd_str = cmd if isinstance(cmd, str) else ' '.join(cmd)
    detail_logger.debug(f"Executing: {cmd_str}")

    try:
        if show_output or verbose:
            result = subprocess.run(cmd, shell=shell, check=check)
            return result.returncode == 0, ""
        else:
            result = subprocess.run(cmd, shell=shell, check=check, capture_output=True, text=True)

            if result.stdout:
                detail_logger.debug(f"STDOUT:\n{result.stdout}")
            if result.stderr:
                detail_logger.debug(f"STDERR:\n{result.stderr}")

            return result.returncode == 0, result.stdout
    except subprocess.CalledProcessError as e:
        detail_logger.error(f"Command failed: {str(e)}")
        return False, str(e)

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
                print(f"\n  [{current}/{total_packages}] Installing {app}...")

            success, _ = run_command(["brew", "install", "--cask", app], check=False,
                                    verbose=(config.output_mode == OutputMode.VERBOSE))

            if config.output_mode != OutputMode.MINIMAL:
                if success:
                    print(f"     [OK] {app} installed")
                else:
                    print(f"     [WARN] {app} may already be installed or failed")

    if cli_tools:
        progress.update_progress(f"Installing {len(cli_tools)} CLI tools...")
        for tool in cli_tools:
            current += 1
            if config.output_mode == OutputMode.MINIMAL:
                print(f"[{current}/{total_packages}] {tool}")
            else:
                print(f"\n  [{current}/{total_packages}] Installing {tool}...")

            success, _ = run_command(["brew", "install", tool], check=False,
                                    verbose=(config.output_mode == OutputMode.VERBOSE))

            if config.output_mode != OutputMode.MINIMAL:
                if success:
                    print(f"     [OK] {tool} installed")
                else:
                    print(f"     [WARN] {tool} may already be installed or failed")

def main():
    """Main setup function with config file support"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Enhanced macOS Development Environment Setup')
    parser.add_argument('-c', '--config', type=Path, help='Configuration file (YAML or JSON)')
    parser.add_argument('-m', '--mode', choices=['minimal', 'normal', 'verbose'],
                       default='normal', help='Output mode')
    parser.add_argument('--no-notifications', action='store_true',
                       help='Disable notifications')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be installed without installing')

    args = parser.parse_args()

    # Load configuration
    config_data = {}
    if args.config and args.config.exists():
        print(f"Loading configuration from: {args.config}")
        config_data = load_config(args.config)

    # Get user configuration
    config = get_user_input_or_config(config_data)

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
        steps.append(("Install/Update Homebrew", lambda: None))  # Placeholder

    if config.config_data.get('packages', {}):
        steps.append(("Install Brew Packages", lambda: install_brew_packages(config, progress)))

    # Add more steps based on config...

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
            input("\nPress Enter to begin...")

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