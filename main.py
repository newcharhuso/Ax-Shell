import os
import gi
gi.require_version("GLib", "2.0")
from gi.repository import GLib, Gio
import setproctitle

from fabric import Application
from fabric.utils import get_relative_path
from config.data import APP_NAME, CONFIG_FILE, CURRENT_WALLPAPER_PATH, load_config
from modules.bar import Bar
from modules.corners import Corners
from modules.dock import Dock
from modules.notch import Notch
from modules.notifications import NotificationPopup
from modules.updater import run_updater

class AxShellApp(Application):
    def __init__(self):
        super().__init__(
            APP_NAME,
            application_id=f"com.github.poogas.{APP_NAME}",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )
        setproctitle.setproctitle(APP_NAME)

        self.ensure_config_file_exists()
        self.ensure_current_wallpaper_exists()
        self.config = load_config()

        self.corners = Corners()
        self.bar = Bar()
        self.notch = Notch()
        self.dock = Dock()
        self.bar.notch = self.notch
        self.notch.bar = self.bar
        self.notification = NotificationPopup(widgets=self.notch.dashboard.widgets)

        self.add_window(self.bar)
        self.add_window(self.notch)
        self.add_window(self.dock)
        self.add_window(self.notification)
        self.add_window(self.corners)

    def do_activate(self):
        super().do_activate()
        corners_visible = self.config.get("corners_visible", True)
        self.corners.set_visible(corners_visible)
        self.set_css()
        GLib.idle_add(run_updater)
        GLib.timeout_add(3600000, run_updater)

    def run_command(self, command: str):
        print(f"Received command: {command}")
        match command:
            case "open_dashboard": self.notch.open_notch("dashboard")
            case "open_launcher": self.notch.open_notch("launcher")
            case "open_bluetooth": self.notch.open_notch("bluetooth")
            case "open_pins": self.notch.open_notch("pins")
            case "open_kanban": self.notch.open_notch("kanban")
            case "open_tmux": self.notch.open_notch("tmux")
            case "open_cliphist": self.notch.open_notch("cliphist")
            case "open_tools": self.notch.open_notch("tools")
            case "open_overview": self.notch.open_notch("overview")
            case "open_wallpapers": self.notch.open_notch("wallpapers")
            case "open_mixer": self.notch.open_notch("mixer")
            case "open_emoji": self.notch.open_notch("emoji")
            case "open_power": self.notch.open_notch("power")
            case "reload_css": self.set_css()
            case "random_wallpaper": self.notch.dashboard.wallpapers.set_random_wallpaper(None, external=True)
            case "toggle_caffeine": self.notch.dashboard.widgets.buttons.caffeine_button.toggle_inhibit(external=True)
            case _:
                print(f"Unknown command: {command}")

    def set_css(self):
        self.set_stylesheet_from_file(get_relative_path("main.css"))

    def ensure_config_file_exists(self):
        if not os.path.isfile(CONFIG_FILE):
            print(f"WARNING: Config file not found at {CONFIG_FILE}")

    def ensure_current_wallpaper_exists(self):
        if not os.path.exists(CURRENT_WALLPAPER_PATH):
            os.makedirs(os.path.dirname(CURRENT_WALLPAPER_PATH), exist_ok=True)
            nix_wallpapers_path = os.getenv("AX_SHELL_WALLPAPERS_DIR_DEFAULT")
            if nix_wallpapers_path:
                source_wallpaper = os.path.join(nix_wallpapers_path, "example-1.jpg")
                if os.path.exists(source_wallpaper):
                    os.symlink(source_wallpaper, CURRENT_WALLPAPER_PATH)
            else:
                print("WARNING: AX_SHELL_WALLPAPERS_DIR_DEFAULT not set.")

if __name__ == "__main__":
    setproctitle.setproctitle(APP_NAME)

    if not os.path.isfile(CONFIG_FILE):
        config_script_path = get_relative_path("config/config.py")
        exec_shell_command_async(f"python {config_script_path}")

    current_wallpaper = os.path.expanduser("~/.current.wall")
    if not os.path.exists(current_wallpaper):
        example_wallpaper = os.path.expanduser(
            f"~/.config/{APP_NAME_CAP}/assets/wallpapers_example/example-1.jpg"
        )
        os.symlink(example_wallpaper, current_wallpaper)

    # Load configuration
    from config.data import load_config

    config = load_config()

    GLib.idle_add(run_updater)
    # Every hour
    GLib.timeout_add(3600000, run_updater)

    # Initialize multi-monitor services
    try:
        from utils.monitor_manager import get_monitor_manager
        from services.monitor_focus import get_monitor_focus_service
        from utils.global_keybinds import init_global_keybind_objects
        
        monitor_manager = get_monitor_manager()
        monitor_focus_service = get_monitor_focus_service()
        monitor_manager.set_monitor_focus_service(monitor_focus_service)
        init_global_keybind_objects()
        
        # Get all available monitors
        all_monitors = monitor_manager.get_monitors()
        multi_monitor_enabled = True
    except ImportError:
        # Fallback to single monitor mode
        all_monitors = [{'id': 0, 'name': 'default'}]
        monitor_manager = None
        multi_monitor_enabled = False
    
    # Filter monitors based on selected_monitors configuration
    selected_monitors_config = config.get("selected_monitors", [])
    
    # If selected_monitors is empty, show on all monitors (current behavior)
    if not selected_monitors_config:
        monitors = all_monitors
        print("Ax-Shell: No specific monitors selected, showing on all monitors")
    else:
        # Filter monitors to only include selected ones
        monitors = []
        selected_monitor_names = set(selected_monitors_config)
        
        for monitor in all_monitors:
            monitor_name = monitor.get('name', f'monitor-{monitor.get("id", 0)}')
            if monitor_name in selected_monitor_names:
                monitors.append(monitor)
                print(f"Ax-Shell: Including monitor '{monitor_name}' (selected)")
            else:
                print(f"Ax-Shell: Excluding monitor '{monitor_name}' (not selected)")
        
        # Fallback: if no valid monitors found, use all monitors
        if not monitors:
            print("Ax-Shell: No valid selected monitors found, falling back to all monitors")
            monitors = all_monitors
    
    # Create application components list
    app_components = []
    corners = None
    notification = None
    
    # Create components for each monitor
    for monitor in monitors:
        monitor_id = monitor['id']
        
        # Create corners only for the first monitor (shared across all)
        if monitor_id == 0:
            corners = Corners()
            # Set corners visibility based on config
            corners_visible = config.get("corners_visible", True)
            corners.set_visible(corners_visible)
            app_components.append(corners)
        
        # Create monitor-specific components
        if multi_monitor_enabled:
            bar = Bar(monitor_id=monitor_id)
            notch = Notch(monitor_id=monitor_id)
            dock = Dock(monitor_id=monitor_id)
        else:
            # Single monitor fallback
            bar = Bar()
            notch = Notch()
            dock = Dock()
        
        # Connect bar and notch
        bar.notch = notch
        notch.bar = bar
        
        # Create notification popup for the first monitor only
        if monitor_id == 0:
            notification = NotificationPopup(widgets=notch.dashboard.widgets)
            app_components.append(notification)
        
        # Register instances in monitor manager if available
        if multi_monitor_enabled and monitor_manager:
            monitor_manager.register_monitor_instances(monitor_id, {
                'bar': bar,
                'notch': notch,
                'dock': dock,
                'corners': corners if monitor_id == 0 else None
            })
        
        # Add components to app list
        app_components.extend([bar, notch, dock])

    # Create the application with all components
    app = Application(f"{APP_NAME}", *app_components)

    def set_css():
        app.set_stylesheet_from_file(
            get_relative_path("main.css"),
        )

    app.set_css = set_css

    app.set_css()

    app.run()
