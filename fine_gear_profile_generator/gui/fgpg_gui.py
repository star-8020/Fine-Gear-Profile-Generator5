import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Import the refactored modules
from ..core import gear_core
from ..io import dxf_exporter, image_exporter
from ..utils import config_manager

SPEC_FIELDS = [
    ("module_m", "Module, m", "[mm], (>0)"),
    ("teeth_number_z", "Teeth Number, z1", "[ea], (+/-)"),
    ("pressure_angle_alpha", "Pressure Angle, alpha", "[deg]"),
    ("offset_factor_x", "Offset Factor, x1", "(-1~+1)"),
    ("backlash_factor_b", "Backlash Factor, b", "(0~1)"),
    ("addendum_factor_a", "Addendum Factor, a", "(0~1)"),
    ("dedendum_factor_d", "Dedendum Factor, d", "(0~1)"),
    ("hob_edge_radius_c", "Hob Edge Radius, c", ""),
    ("tooth_edge_radius_e", "Tooth Edge Radius, e", "")
]

MATING_FIELDS = [
    ("teeth_number_z2", "Teeth Number, z2", "[ea]"),
    ("offset_factor_x2", "Offset Factor, x2", "")
]

GRAPHIC_FIELDS = [
    ("x_0", "Center, x_0", "[mm]"),
    ("y_0", "Center, y_0", "[mm]"),
    ("seg_involute", "Seg, involute", "[ea]"),
    ("seg_edge_r", "Seg, edge_r", "[ea]"),
    ("seg_root_r", "Seg, root_r", "[ea]"),
    ("seg_outer", "Seg, outer", "[ea]"),
    ("seg_root", "Seg, root", "[ea]")
]

class GearApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.config_data = config_manager.load_app_config()
        self.defaults = config_manager.get_defaults(self.config_data)

        window_config = self.config_data.get('window', {})
        self.title(window_config.get('title', "FGPG - Fine Gear Profile Generator (Refactored)"))
        self.geometry(window_config.get('geometry', "950x700"))

        self.vars = {}
        self.current_image_path = self.defaults.get('current_image_path', "Result1.png")
        self.logo_image = None
        self.result_image = None

        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        left_frame = ttk.Frame(main_frame, padding="10")
        left_frame.grid(row=0, column=0, sticky="ns")
        right_frame = ttk.Frame(main_frame, padding="10")
        right_frame.grid(row=0, column=1, sticky="ns")
        main_frame.grid_columnconfigure(1, weight=1)

        self.create_spec_widgets(left_frame)
        self.create_mating_gear_widgets(left_frame)
        self.create_analysis_widgets(left_frame)
        self.create_graphics_widgets(left_frame)
        self.create_control_widgets(right_frame)
        self.load_logo_image()

    def create_entry(self, parent, row, key, label, default_val, unit):
        ttk.Label(parent, text=f"{label} =").grid(row=row, column=0, sticky="w", pady=2)
        var = tk.StringVar(value=str(default_val))
        self.vars[key] = var
        ttk.Entry(parent, textvariable=var, width=10).grid(row=row, column=1, padx=5)
        ttk.Label(parent, text=unit).grid(row=row, column=2, sticky="w")

    def create_spec_widgets(self, parent):
        frame = ttk.LabelFrame(parent, text="1. Gear Spec (Gear 1)", padding="10")
        frame.grid(row=0, column=0, sticky="ew", pady=5)
        for i, (key, label, unit) in enumerate(SPEC_FIELDS):
            default_val = self.defaults.get(key)
            self.create_entry(frame, i, key, label, default_val, unit)

    def create_mating_gear_widgets(self, parent):
        frame = ttk.LabelFrame(parent, text="1.5. Mating Gear Spec (Gear 2)", padding="10")
        frame.grid(row=1, column=0, sticky="ew", pady=5)
        for i, (key, label, unit) in enumerate(MATING_FIELDS):
            default_val = self.defaults.get(key)
            self.create_entry(frame, i, key, label, default_val, unit)

    def create_analysis_widgets(self, parent):
        frame = ttk.LabelFrame(parent, text="Analysis", padding="10")
        frame.grid(row=2, column=0, sticky="ew", pady=5)
        ttk.Label(frame, text="Contact Ratio:").grid(row=0, column=0, sticky="w")
        self.vars['contact_ratio'] = tk.StringVar(value="--")
        ttk.Label(frame, textvariable=self.vars['contact_ratio'], font=("TkDefaultFont", 10, "bold")).grid(row=0, column=1, sticky="w")
        ttk.Label(frame, text="Center Distance:").grid(row=1, column=0, sticky="w")
        self.vars['center_distance'] = tk.StringVar(value="--")
        ttk.Label(frame, textvariable=self.vars['center_distance']).grid(row=1, column=1, sticky="w")

    def create_graphics_widgets(self, parent):
        frame = ttk.LabelFrame(parent, text="2. Graphics & Misc.", padding="10")
        frame.grid(row=3, column=0, sticky="ew", pady=5)
        for i, (key, label, unit) in enumerate(GRAPHIC_FIELDS):
            default_val = self.defaults.get(key)
            self.create_entry(frame, i, key, label, default_val, unit)

    def create_control_widgets(self, parent):
        dir_frame = ttk.Frame(parent)
        dir_frame.grid(row=0, column=0, sticky="ew", pady=5)
        ttk.Label(dir_frame, text="Working Directory:").grid(row=0, column=0, sticky="w")
        default_working_dir = self.defaults.get('working_directory', "./result/")
        self.vars['working_directory'] = tk.StringVar(value=default_working_dir)
        ttk.Entry(dir_frame, textvariable=self.vars['working_directory'], width=40).grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(dir_frame, text="Browse...", command=self.browse_dir).grid(row=0, column=2)
        dir_frame.columnconfigure(1, weight=1)

        self.image_label = ttk.Label(parent, text="Image will be displayed here.")
        self.image_label.grid(row=1, column=0, pady=10, sticky="nsew")
        parent.rowconfigure(1, weight=1)

        self.status_var = tk.StringVar(value="Welcome to the refactored Fine Gear Profile Generator!")
        ttk.Label(parent, textvariable=self.status_var, wraplength=500).grid(row=2, column=0, sticky="ew", pady=5)

        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=3, column=0, sticky="ew")
        ttk.Button(btn_frame, text="Load", command=self.load_params_from_file).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Run", command=self.run_calculation).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Save", command=self.save_params_to_file).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Exit", command=self.quit).pack(side="left", padx=5)

    def load_logo_image(self):
        if not PIL_AVAILABLE:
            self.image_label.config(text="Pillow library not found. Image preview is disabled.")
            return
        # The logo is now in the parent directory of the project root
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'FGPG2-05', 'FGPG2.png')
        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                img.thumbnail((500, 500))
                self.logo_image = ImageTk.PhotoImage(img)
                self.image_label.config(image=self.logo_image)
            except Exception as e:
                self.status_var.set(f"Info: Could not load logo. {e}")
        else:
            self.status_var.set("Info: Logo image not found.")

    def browse_dir(self):
        dir_name = filedialog.askdirectory()
        if dir_name:
            self.vars['working_directory'].set(dir_name)

    def get_params_from_ui(self):
        try:
            params = {
                'M': float(self.vars['module_m'].get()), 'Z': int(self.vars['teeth_number_z'].get()),
                'ALPHA': float(self.vars['pressure_angle_alpha'].get()), 'X': float(self.vars['offset_factor_x'].get()),
                'B': float(self.vars['backlash_factor_b'].get()), 'A': float(self.vars['addendum_factor_a'].get()),
                'D': float(self.vars['dedendum_factor_d'].get()), 'C': float(self.vars['hob_edge_radius_c'].get()),
                'E': float(self.vars['tooth_edge_radius_e'].get()), 'X_0': float(self.vars['x_0'].get()),
                'Y_0': float(self.vars['y_0'].get()),
                'SEG_INVOLUTE': int(self.vars['seg_involute'].get()), 'SEG_EDGE_R': int(self.vars['seg_edge_r'].get()),
                'SEG_ROOT_R': int(self.vars['seg_root_r'].get()), 'SEG_OUTER': int(self.vars['seg_outer'].get()),
                'SEG_ROOT': int(self.vars['seg_root'].get()),
                'z2': int(self.vars['teeth_number_z2'].get()), 'x2': float(self.vars['offset_factor_x2'].get())
            }
            return params
        except (ValueError, KeyError) as e:
            messagebox.showerror("Input Error", f"Invalid or missing input value for {e}")
            return None

    def run_calculation(self):
        params = self.get_params_from_ui()
        if not params: return

        working_dir = self.vars['working_directory'].get()
        os.makedirs(working_dir, exist_ok=True)

        try:
            result = gear_core.generate_gear_pair(params)

            analysis = result['analysis']
            gear1 = result['gear1']
            gear2 = result['gear2']

            image_exporter.export_gear_pair_to_image(
                working_dir,
                gear1['profile'],
                gear2['profile'],
                analysis['center_distance'],
                params['M'],
                params['Z'],
                params['z2'],
                params['X_0'],
                params['Y_0']
            )

            dxf_exporter.export_gear_pair_to_dxf(
                working_dir,
                gear1['profile'],
                gear2['profile'],
                analysis['center_distance'],
                params['X_0'],
                params['Y_0']
            )

            self.vars['contact_ratio'].set(f"{analysis['contact_ratio']:.4f}")
            self.vars['center_distance'].set(f"{analysis['center_distance']:.4f} mm")
            self.status_var.set(
                f"Run: OK. G1 Undercut: {gear1['undercut_status']}. G2 Undercut: {gear2['undercut_status']}"
            )
            self.display_result_image()

        except Exception as e:
            messagebox.showerror("Calculation Error", f"An error occurred: {e}")
            self.status_var.set(f"Run: Failed. {e}")

    def display_result_image(self):
        if not PIL_AVAILABLE:
            self.status_var.set("Run: OK. Install Pillow (pip install Pillow) for image preview.")
            return
        try:
            working_dir = self.vars['working_directory'].get()
            img_path = os.path.join(working_dir, self.current_image_path)
            if os.path.exists(img_path):
                img = Image.open(img_path)
                img.thumbnail((500, 500))
                self.result_image = ImageTk.PhotoImage(img)
                self.image_label.config(image=self.result_image)
            else:
                # If image not found, revert to logo
                self.image_label.config(image=self.logo_image)
                self.status_var.set(f"Image not found: {img_path}")
        except Exception as e:
            self.status_var.set(f"Error displaying image: {e}")

    def save_params_to_file(self):
        working_dir = self.vars['working_directory'].get()
        data_to_save = {key: var.get() for key, var in self.vars.items() if key != 'working_directory'}
        success, message = config_manager.save_params(working_dir, data_to_save)
        self.status_var.set(message)
        if not success:
            messagebox.showerror("Save Error", message)

    def load_params_from_file(self):
        working_dir = self.vars['working_directory'].get()
        success, data_or_error = config_manager.load_params(working_dir)
        if success:
            for key, value in data_or_error.items():
                if key in self.vars:
                    self.vars[key].set(value)
            self.status_var.set("Load: OK")
        else:
            messagebox.showerror("Load Error", data_or_error)
            self.status_var.set(f"Load failed: {data_or_error}")