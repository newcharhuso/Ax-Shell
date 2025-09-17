import json
import os

import gi

gi.require_version("Gtk", "3.0")
from fabric.utils.helpers import get_relative_path
from gi.repository import Gdk, GLib

APP_NAME = "ax-shell"
APP_NAME_CAP = "Ax-Shell"


PANEL_POSITION_KEY = "panel_position"
PANEL_POSITION_DEFAULT = "Center"
NOTIF_POS_KEY = "notif_pos"
NOTIF_POS_DEFAULT = "Top"

CACHE_DIR = str(GLib.get_user_cache_dir()) + f"/{APP_NAME}"

USERNAME = os.getlogin()
HOSTNAME = os.uname().nodename
HOME_DIR = os.path.expanduser("~")

XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
XDG_STATE_HOME = os.environ.get("XDG_STATE_HOME", os.path.expanduser("~/.local/state"))
STATE_DIR = os.path.join(XDG_STATE_HOME, APP_NAME)
os.makedirs(STATE_DIR, exist_ok=True)

screen = Gdk.Screen.get_default()
CURRENT_WIDTH = screen.get_width()
CURRENT_HEIGHT = screen.get_height()

CURRENT_WALLPAPER_PATH = os.path.join(XDG_CONFIG_HOME, "ax-shell/current.wall")
WALLPAPERS_DIR_DEFAULT = os.environ.get("AX_SHELL_WALLPAPERS_DIR_DEFAULT", get_relative_path("../assets/wallpapers_example"))
CONFIG_FILE = os.environ.get("AX_SHELL_CONFIG_FILE", get_relative_path("../config/config.json"))
MATUGEN_STATE_FILE = os.path.join(STATE_DIR, "matugen")


BAR_WORKSPACE_USE_CHINESE_NUMERALS = False
BAR_THEME = "Pills"

DOCK_THEME = "Pills"

PANEL_THEME = "Notch"
DATETIME_12H_FORMAT = False


def load_config():
    """Load the configuration from config.json"""
    config_path = CONFIG_FILE
    config = {}

    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")

    return config


# Import defaults from settings_constants to avoid duplication
from .settings_constants import DEFAULTS

# Load configuration once and use throughout the module
config = {}
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
    
    WALLPAPERS_DIR = config.get("wallpapers_dir", WALLPAPERS_DIR_DEFAULT)
    BAR_POSITION = config.get("bar_position", "Top")
    VERTICAL = BAR_POSITION in ["Left", "Right"]
    CENTERED_BAR = config.get("centered_bar", False)
    DATETIME_12H_FORMAT = config.get("datetime_12h_format", False)
    TERMINAL_COMMAND = config.get("terminal_command", "kitty -e")
    DOCK_ENABLED = config.get("dock_enabled", True)
    DOCK_ALWAYS_OCCLUDED = config.get("dock_always_occluded", False)
    DOCK_ICON_SIZE = config.get("dock_icon_size", 28)
    BAR_WORKSPACE_SHOW_NUMBER = config.get("bar_workspace_show_number", False)
    BAR_WORKSPACE_USE_CHINESE_NUMERALS = config.get(
        "bar_workspace_use_chinese_numerals", False
    )
    BAR_HIDE_SPECIAL_WORKSPACE = config.get("bar_hide_special_workspace", True)
    BAR_THEME = config.get("bar_theme", "Pills")
    DOCK_THEME = config.get("dock_theme", "Pills")
    PANEL_THEME = config.get("panel_theme", "Pills")

# Set configuration values using defaults from settings_constants
WALLPAPERS_DIR = config.get("wallpapers_dir", DEFAULTS["wallpapers_dir"])
BAR_POSITION = config.get("bar_position", DEFAULTS["bar_position"])
VERTICAL = BAR_POSITION in ["Left", "Right"]
CENTERED_BAR = config.get("centered_bar", DEFAULTS["centered_bar"])
DATETIME_12H_FORMAT = config.get("datetime_12h_format", DEFAULTS["datetime_12h_format"])
TERMINAL_COMMAND = config.get("terminal_command", DEFAULTS["terminal_command"])
DOCK_ENABLED = config.get("dock_enabled", DEFAULTS["dock_enabled"])
DOCK_ALWAYS_OCCLUDED = config.get("dock_always_occluded", DEFAULTS["dock_always_occluded"])
DOCK_ICON_SIZE = config.get("dock_icon_size", DEFAULTS["dock_icon_size"])
BAR_WORKSPACE_SHOW_NUMBER = config.get("bar_workspace_show_number", DEFAULTS["bar_workspace_show_number"])
BAR_WORKSPACE_USE_CHINESE_NUMERALS = config.get("bar_workspace_use_chinese_numerals", DEFAULTS["bar_workspace_use_chinese_numerals"])
BAR_HIDE_SPECIAL_WORKSPACE = config.get("bar_hide_special_workspace", DEFAULTS["bar_hide_special_workspace"])
BAR_THEME = config.get("bar_theme", DEFAULTS["bar_theme"])
DOCK_THEME = config.get("dock_theme", DEFAULTS["dock_theme"])
PANEL_THEME = config.get("panel_theme", DEFAULTS["panel_theme"])

PANEL_POSITION = config.get(PANEL_POSITION_KEY, DEFAULTS[PANEL_POSITION_KEY])
NOTIF_POS = config.get(NOTIF_POS_KEY, DEFAULTS[NOTIF_POS_KEY])

    BAR_METRICS_DISKS = config.get("bar_metrics_disks", ["/"])
    METRICS_VISIBLE = config.get(
        "metrics_visible", {"cpu": True, "ram": True, "disk": True, "gpu": True}
    )
    METRICS_SMALL_VISIBLE = config.get(
        "metrics_small_visible", {"cpu": True, "ram": True, "disk": True, "gpu": True}
    )
else:
    WALLPAPERS_DIR = WALLPAPERS_DIR_DEFAULT
    BAR_POSITION = "Top"
    VERTICAL = False
    CENTERED_BAR = False
    DATETIME_12H_FORMAT = False
    DOCK_ENABLED = True
    DOCK_ALWAYS_OCCLUDED = False
    TERMINAL_COMMAND = "kitty -e"
    DOCK_ICON_SIZE = 28
    BAR_WORKSPACE_SHOW_NUMBER = False
    BAR_WORKSPACE_USE_CHINESE_NUMERALS = False
    BAR_HIDE_SPECIAL_WORKSPACE = True
    BAR_THEME = "Pills"
    DOCK_THEME = "Pills"
    PANEL_THEME = "Notch"

BAR_METRICS_DISKS = config.get("bar_metrics_disks", DEFAULTS["bar_metrics_disks"])
METRICS_VISIBLE = config.get("metrics_visible", DEFAULTS["metrics_visible"])
METRICS_SMALL_VISIBLE = config.get("metrics_small_visible", DEFAULTS["metrics_small_visible"])
SELECTED_MONITORS = config.get("selected_monitors", DEFAULTS["selected_monitors"])
