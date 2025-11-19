"""
PCR系统 - 纯GUI版本
移除了所有硬件控制代码(TMC2209, TEC, GPIO, ADC等)
仅保留Kivy/KivyMD界面框架
"""

from kivy.metrics import dp
from kivy.config import Config
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.anchorlayout import AnchorLayout
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.fitimage import FitImage
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.textfield import MDTextField, MDTextFieldLeadingIcon, MDTextFieldHintText
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, MDListItem, MDListItemLeadingIcon, MDListItemHeadlineText
from kivymd.uix.dialog import MDDialog, MDDialogIcon, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer

from datetime import datetime
from io import BytesIO
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time
import csv
import os
import json

Config.set('kivy', 'keyboard_mode', 'systemanddock')

USER_DATA_FILE = os.path.expanduser("~/user_data.json")

def load_users():
    if not os.path.exists(USER_DATA_FILE):
        return {"users": []}
    with open(USER_DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except Exception:
            return {"users": []}

def save_users(data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def export_to_csv(data_records, filename='data_records.csv'):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['elapsed', 'cy5_avg_value1', 'cy5_avg_value2', 'cy5_avg_value3',
                      'fam_avg_value1', 'fam_avg_value2', 'fam_avg_value3', 'hex_value']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for record in data_records:
            row_data = {
                'elapsed': record['elapsed'],
                'cy5_avg_value1': record['cy5_avg_values'][0],
                'cy5_avg_value2': record['cy5_avg_values'][1],
                'cy5_avg_value3': record['cy5_avg_values'][2],
                'fam_avg_value1': record['fam_avg_values'][0],
                'fam_avg_value2': record['fam_avg_values'][1],
                'fam_avg_value3': record['fam_avg_values'][2],
                'hex_value': record['hex_value'],
            }
            writer.writerow(row_data)

# ==================== 自定义UI组件 ====================
class CircularProgressBar(Widget):
    percentage = NumericProperty(0)
    bar_color = (0.2, 0.6, 1, 1)
    background_color = (0.3, 0.3, 0.3, 0.3)
    bar_width = NumericProperty(10)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas, percentage=self.update_canvas)
        Clock.schedule_once(self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(*self.background_color)
            Ellipse(pos=self.pos, size=self.size, angle_start=0, angle_end=360)
            Color(*self.bar_color)
            angle = 360 * (self.percentage / 100)
            Ellipse(pos=self.pos, size=self.size, angle_start=90, angle_end=90 + angle)

class ProcessFlow(Widget):
    fill_percentage = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas, fill_percentage=self.update_canvas)
        Clock.schedule_once(self.update_canvas)
    
    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0.5, 0.5, 0.5, 1)
            Line(rectangle=(self.x, self.y, self.width, self.height), width=2)
            fill_height = self.height * (self.fill_percentage / 100)
            Color(0.2, 0.6, 1, 0.5)
            Rectangle(pos=(self.x, self.y), size=(self.width, fill_height))

# ==================== 界面类 ====================
class HomingScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDFloatLayout()
        
        tip = MDLabel(
            text="System Initializing...",
            halign="center", font_style="Title",
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        layout.add_widget(tip)
        self.add_widget(layout)

    def on_enter(self, *args):
        Clock.schedule_once(self._mock_homing, 0.5)

    def _mock_homing(self, dt):
        app = MDApp.get_running_app()
        app.homed_ok = True
        app.root.current = "lock"

class LockScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.users = load_users()["users"]
        self.current_index = 0

        layout = MDFloatLayout()

        self.user_label = MDLabel(
            text=self.get_current_user_name(),
            halign="center",
            font_style="Title",
            pos_hint={"center_x": 0.5, "center_y": 0.65},
            size_hint=(None, None)
        )
        layout.add_widget(self.user_label)

        left_btn = MDButton(
            MDButtonText(text="<",font_style="Title"),
            pos_hint={"center_x": 0.35, "center_y": 0.65},
            size_hint=(0.15, 0.1),
            on_release=self.prev_user
        )
        right_btn = MDButton(
            MDButtonText(text=">",font_style="Title"),
            pos_hint={"center_x": 0.65, "center_y": 0.65},
            size_hint=(0.15, 0.1),
            on_release=self.next_user
        )
        layout.add_widget(left_btn)
        layout.add_widget(right_btn)

        create_btn = MDButton(
            MDButtonText(text="Create User",font_style="Title"),
            pos_hint={"center_x": 0.85, "center_y": 0.1},
            size_hint=(0.4, 0.1),
            on_release=self.go_to_create_user
        )
        layout.add_widget(create_btn)

        login_btn = MDButton(
            MDButtonText(text="Login",font_style="Title"),
            pos_hint={"center_x": 0.5, "center_y": 0.3},
            size_hint=(0.4, 0.1),
            on_release=self.go_to_login
        )
        layout.add_widget(login_btn)

        self.add_widget(layout)

    def get_current_user_name(self):
        if not self.users:
            return "No Users"
        return self.users[self.current_index]["username"]

    def prev_user(self, *args):
        if self.users:
            self.current_index = (self.current_index - 1) % len(self.users)
            self.user_label.text = self.get_current_user_name()

    def next_user(self, *args):
        if self.users:
            self.current_index = (self.current_index + 1) % len(self.users)
            self.user_label.text = self.get_current_user_name()

    def go_to_login(self, *args):
        if not self.users:
            snackbar = MDSnackbar(MDSnackbarText(text="No users. Please create one."),
                                  y=dp(24), pos_hint={"center_x": 0.5}, size_hint_x=0.8)
            snackbar.open()
            return
        app = MDApp.get_running_app()
        app.root.get_screen('user_login').selected_username = self.get_current_user_name()
        app.root.current = 'user_login'

    def go_to_create_user(self, *args):
        self.manager.current = 'create_user'

    def on_enter(self, *args):
        self.users = load_users()["users"]
        self.current_index = 0
        self.user_label.text = self.get_current_user_name()

class UserLoginScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_username = ""

        layout = MDFloatLayout()

        back_btn = MDIconButton(
            icon="arrow-left",
            pos_hint={"x": 0.02, "top": 0.98},
            on_release=lambda x: setattr(self.manager, 'current', 'lock')
        )
        layout.add_widget(back_btn)

        self.username_label = MDLabel(
            text="Username",
            halign="center",
            font_style="Title",
            pos_hint={"center_x": 0.5, "center_y": 0.7},
        )
        layout.add_widget(self.username_label)

        self.password_field = MDTextField(
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            size_hint=(0.7, None),
            height=dp(50),
            password=True
        )
        self.password_field.add_widget(MDTextFieldLeadingIcon(icon="lock"))
        self.password_field.add_widget(MDTextFieldHintText(text="Enter Password"))
        layout.add_widget(self.password_field)

        login_btn = MDButton(
            MDButtonText(text="Login"),
            pos_hint={"center_x": 0.5, "center_y": 0.3},
            size_hint=(0.5, None),
            height=dp(50),
            on_release=self.login
        )
        layout.add_widget(login_btn)

        self.add_widget(layout)

    def on_enter(self, *args):
        self.username_label.text = f"User: {self.selected_username}"
        self.password_field.text = ""

    def login(self, *args):
        password = self.password_field.text.strip()
        data = load_users()
        for user in data.get("users", []):
            if user["username"] == self.selected_username and user["password"] == password:
                app = MDApp.get_running_app()
                app.current_user = self.selected_username
                self.manager.current = "main"
                return
        
        snackbar = MDSnackbar(MDSnackbarText(text="Incorrect password"),
                              y=dp(24), pos_hint={"center_x": 0.5}, size_hint_x=0.8)
        snackbar.open()

class CreateUserScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = MDFloatLayout()
        
        back_btn = MDIconButton(
            icon="arrow-left",
            pos_hint={"x": 0.02, "top": 0.98},
            on_release=lambda x: setattr(self.manager, 'current', 'lock')
        )
        layout.add_widget(back_btn)
        
        title = MDLabel(
            text="Create New User",
            halign="center",
            font_style="Title",
            pos_hint={"center_x": 0.5, "center_y": 0.8}
        )
        layout.add_widget(title)
        
        self.username_field = MDTextField(
            pos_hint={"center_x": 0.5, "center_y": 0.6},
            size_hint=(0.7, None),
            height=dp(50)
        )
        self.username_field.add_widget(MDTextFieldLeadingIcon(icon="account"))
        self.username_field.add_widget(MDTextFieldHintText(text="Username"))
        layout.add_widget(self.username_field)
        
        self.password_field = MDTextField(
            pos_hint={"center_x": 0.5, "center_y": 0.45},
            size_hint=(0.7, None),
            height=dp(50),
            password=True
        )
        self.password_field.add_widget(MDTextFieldLeadingIcon(icon="lock"))
        self.password_field.add_widget(MDTextFieldHintText(text="Password"))
        layout.add_widget(self.password_field)
        
        create_btn = MDButton(
            MDButtonText(text="Create"),
            pos_hint={"center_x": 0.5, "center_y": 0.25},
            size_hint=(0.5, None),
            height=dp(50),
            on_release=self.create_user
        )
        layout.add_widget(create_btn)
        
        self.add_widget(layout)
    
    def create_user(self, *args):
        username = self.username_field.text.strip()
        password = self.password_field.text.strip()
        
        if not username or not password:
            snackbar = MDSnackbar(MDSnackbarText(text="Please enter username and password"),
                                  y=dp(24), pos_hint={"center_x": 0.5}, size_hint_x=0.8)
            snackbar.open()
            return
        
        data = load_users()
        for user in data.get("users", []):
            if user["username"] == username:
                snackbar = MDSnackbar(MDSnackbarText(text="Username already exists"),
                                      y=dp(24), pos_hint={"center_x": 0.5}, size_hint_x=0.8)
                snackbar.open()
                return
        
        data["users"].append({"username": username, "password": password})
        save_users(data)
        
        snackbar = MDSnackbar(MDSnackbarText(text="User created successfully!"),
                              y=dp(24), pos_hint={"center_x": 0.5}, size_hint_x=0.8)
        snackbar.open()
        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'lock'), 1.5)

class MainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = MDFloatLayout()
        
        top_bar = MDBoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=dp(60),
            pos_hint={"top": 1},
            padding=[dp(10), dp(10)],
            spacing=dp(10)
        )
        
        self.user_label = MDLabel(
            text="User: Guest",
            size_hint=(0.7, 1)
        )
        top_bar.add_widget(self.user_label)
        
        lock_btn = MDIconButton(
            icon="lock",
            on_release=lambda x: setattr(self.manager, 'current', 'lock')
        )
        top_bar.add_widget(lock_btn)
        layout.add_widget(top_bar)
        
        card_container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(20),
            padding=[dp(40), dp(100), dp(40), dp(40)],
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        
        new_exp_card = MDCard(
            size_hint=(1, None),
            height=dp(150),
            style="elevated",
            on_release=lambda x: setattr(self.manager, 'current', 'pretest')
        )
        new_exp_content = MDBoxLayout(orientation="vertical", padding=dp(20), spacing=dp(10))
        new_exp_content.add_widget(MDLabel(text="New Experiment", font_style="Title", role="large", halign="center"))
        new_exp_content.add_widget(MDLabel(text="Start a new PCR experiment", halign="center"))
        new_exp_card.add_widget(new_exp_content)
        card_container.add_widget(new_exp_card)
        
        history_card = MDCard(
            size_hint=(1, None),
            height=dp(150),
            style="elevated",
            on_release=lambda x: setattr(self.manager, 'current', 'report')
        )
        history_content = MDBoxLayout(orientation="vertical", padding=dp(20), spacing=dp(10))
        history_content.add_widget(MDLabel(text="History", font_style="Title", role="large", halign="center"))
        history_content.add_widget(MDLabel(text="View past results", halign="center"))
        history_card.add_widget(history_content)
        card_container.add_widget(history_card)
        
        layout.add_widget(card_container)
        self.add_widget(layout)
    
    def on_enter(self):
        app = MDApp.get_running_app()
        if hasattr(app, 'current_user'):
            self.user_label.text = f"User: {app.current_user}"

class PreTestScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = MDFloatLayout()
        
        back_btn = MDIconButton(
            icon="arrow-left",
            pos_hint={"x": 0.02, "top": 0.98},
            on_release=lambda x: setattr(self.manager, 'current', 'main')
        )
        layout.add_widget(back_btn)
        
        main_container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(20),
            padding=[dp(40), dp(80), dp(40), dp(40)],
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        
        title = MDLabel(
            text="Experiment Setup",
            font_style="Display",
            role="small",
            halign="center",
            size_hint_y=None,
            height=dp(60)
        )
        main_container.add_widget(title)
        
        self.name_field = MDTextField(size_hint=(1, None), height=dp(50))
        self.name_field.add_widget(MDTextFieldLeadingIcon(icon="text"))
        self.name_field.add_widget(MDTextFieldHintText(text="Project Name"))
        main_container.add_widget(self.name_field)
        
        start_btn = MDButton(
            MDButtonText(text="Start"),
            size_hint=(1, None),
            height=dp(50),
            on_release=self.start_experiment
        )
        main_container.add_widget(start_btn)
        
        layout.add_widget(main_container)
        self.add_widget(layout)
    
    def start_experiment(self, *args):
        if not self.name_field.text.strip():
            snackbar = MDSnackbar(MDSnackbarText(text="Please enter project name"),
                                  y=dp(24), pos_hint={"center_x": 0.5}, size_hint_x=0.8)
            snackbar.open()
            return
        
        app = MDApp.get_running_app()
        app.current_project = self.name_field.text.strip()
        self.manager.current = "instruction"

class InstructionScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = MDFloatLayout()
        
        back_btn = MDIconButton(
            icon="arrow-left",
            pos_hint={"x": 0.02, "top": 0.98},
            on_release=lambda x: setattr(self.manager, 'current', 'pretest')
        )
        layout.add_widget(back_btn)
        
        main_container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(20),
            padding=[dp(40), dp(80), dp(40), dp(40)],
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        
        title = MDLabel(
            text="Instructions",
            font_style="Display",
            role="small",
            halign="center",
            size_hint_y=None,
            height=dp(60)
        )
        main_container.add_widget(title)
        
        instructions = MDLabel(
            text="1. Load samples\n2. Check system\n3. Click Continue",
            halign="center",
            size_hint_y=None,
            height=dp(200)
        )
        main_container.add_widget(instructions)
        
        continue_btn = MDButton(
            MDButtonText(text="Continue"),
            size_hint=(1, None),
            height=dp(50),
            on_release=lambda x: setattr(self.manager, 'current', 'isothermal')
        )
        main_container.add_widget(continue_btn)
        
        layout.add_widget(main_container)
        self.add_widget(layout)

class MotorControlScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.locked = False
        self.stop_requested = False
        self.current_cycle = 0
        self.total_cycles = 40
        self.data_records = []
        
        layout = MDFloatLayout()
        
        top_bar = MDBoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=dp(60),
            pos_hint={"top": 1},
            padding=[dp(10), dp(10)],
            spacing=dp(10)
        )
        
        self.back_button = MDIconButton(icon="arrow-left", on_release=self.go_back)
        top_bar.add_widget(self.back_button)
        
        self.status_label = MDLabel(text="Ready", size_hint=(0.7, 1))
        top_bar.add_widget(self.status_label)
        
        self.stop_button = MDIconButton(icon="stop", disabled=True, on_release=self.stop_experiment)
        top_bar.add_widget(self.stop_button)
        
        layout.add_widget(top_bar)
        
        center_container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(20),
            padding=[dp(40), dp(80), dp(40), dp(120)],
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        
        self.progress_label = MDLabel(
            text="Cycle: 0 / 40",
            font_style="Title",
            role="large",
            halign="center",
            size_hint_y=None,
            height=dp(60)
        )
        center_container.add_widget(self.progress_label)
        
        self.progress_bar = CircularProgressBar(
            size_hint=(None, None),
            size=(dp(200), dp(200)),
            pos_hint={"center_x": 0.5}
        )
        center_container.add_widget(self.progress_bar)
        
        self.temp_label = MDLabel(
            text="Temp: 25°C",
            halign="center",
            size_hint_y=None,
            height=dp(40)
        )
        center_container.add_widget(self.temp_label)
        
        layout.add_widget(center_container)
        
        bottom_container = MDBoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=dp(60),
            pos_hint={"center_x": 0.5, "y": 0.05},
            padding=[dp(40), 0],
            spacing=dp(20)
        )
        
        self.start_button = MDButton(
            MDButtonText(text="Start"),
            size_hint=(0.5, 1),
            on_release=self.start_experiment
        )
        bottom_container.add_widget(self.start_button)
        
        self.step3_button = MDButton(
            MDButtonText(text="View Report"),
            size_hint=(0.5, 1),
            disabled=True,
            on_release=lambda x: setattr(self.manager, 'current', 'report')
        )
        bottom_container.add_widget(self.step3_button)
        
        layout.add_widget(bottom_container)
        self.add_widget(layout)
    
    def go_back(self, *args):
        if not self.locked:
            self.manager.current = "instruction"
    
    def start_experiment(self, *args):
        if self.locked:
            return
        
        self.locked = True
        self.stop_requested = False
        self.current_cycle = 0
        self.data_records = []
        
        self.start_button.disabled = True
        self.stop_button.disabled = False
        self.back_button.disabled = True
        self.step3_button.disabled = True
        
        self.status_label.text = "Running..."
        Clock.schedule_interval(self.simulate_cycle, 1.0)
    
    def simulate_cycle(self, dt):
        if self.stop_requested:
            Clock.unschedule(self.simulate_cycle)
            self.status_label.text = "Stopped"
            self.unlock_ui()
            return
        
        cy5_data = [np.random.uniform(100, 500) for _ in range(3)]
        fam_data = [np.random.uniform(100, 500) for _ in range(3)]
        hex_data = np.random.uniform(100, 500)
        
        self.data_records.append({
            'elapsed': self.current_cycle,
            'cy5_avg_values': cy5_data,
            'fam_avg_values': fam_data,
            'hex_value': hex_data
        })
        
        self.current_cycle += 1
        self.progress_label.text = f"Cycle: {self.current_cycle} / {self.total_cycles}"
        self.progress_bar.percentage = (self.current_cycle / self.total_cycles) * 100
        self.temp_label.text = f"Temp: {60 + np.random.uniform(-0.5, 0.5):.1f}°C"
        
        if self.current_cycle >= self.total_cycles:
            Clock.unschedule(self.simulate_cycle)
            self.complete_experiment()
    
    def stop_experiment(self, *args):
        self.stop_requested = True
    
    def complete_experiment(self):
        self.status_label.text = "Complete!"
        self.save_results()
        self.unlock_ui()
    
    def save_results(self):
        app = MDApp.get_running_app()
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = getattr(app, 'current_project', 'Unnamed')
        base = f"{project_name}_{ts}"
        
        save_dir = os.path.expanduser("~/csv_files")
        os.makedirs(save_dir, exist_ok=True)
        
        csv_path = os.path.join(save_dir, f"{base}_data.csv")
        export_to_csv(self.data_records, filename=csv_path)
        
        app.last_csv = csv_path
        app.last_project = project_name
        app.last_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"Results saved: {csv_path}")
    
    def unlock_ui(self):
        self.locked = False
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.back_button.disabled = False
        self.step3_button.disabled = False

class ReportScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = MDFloatLayout()
        
        back_btn = MDIconButton(
            icon="arrow-left",
            pos_hint={"x": 0.02, "top": 0.98},
            on_release=lambda x: setattr(self.manager, 'current', 'main')
        )
        layout.add_widget(back_btn)
        
        title = MDLabel(
            text="Experiment Reports",
            font_style="Display",
            role="small",
            halign="center",
            pos_hint={"center_x": 0.5, "top": 0.95},
            size_hint_y=None,
            height=dp(60)
        )
        layout.add_widget(title)
        
        scroll = MDScrollView(
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            size_hint=(0.9, 0.75)
        )
        
        self.report_list = MDList()
        scroll.add_widget(self.report_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def on_enter(self):
        self.refresh_list()
    
    def refresh_list(self):
        self.report_list.clear_widgets()
        
        app = MDApp.get_running_app()
        
        if hasattr(app, 'last_project'):
            item = MDListItem()
            item.add_widget(MDListItemLeadingIcon(icon="file-document"))
            item.add_widget(MDListItemHeadlineText(text=f"{app.last_project} - {app.last_time}"))
            self.report_list.add_widget(item)
        else:
            empty_label = MDLabel(text="No data", halign="center")
            self.report_list.add_widget(empty_label)

class MainApp(MDApp):
    def build(self):
        sm = MDScreenManager()
        
        sm.add_widget(HomingScreen(name="homing"))
        sm.add_widget(LockScreen(name="lock"))
        sm.add_widget(UserLoginScreen(name="user_login"))
        sm.add_widget(CreateUserScreen(name="create_user"))
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(PreTestScreen(name="pretest"))
        sm.add_widget(InstructionScreen(name="instruction"))
        sm.add_widget(MotorControlScreen(name="isothermal"))
        sm.add_widget(ReportScreen(name="report"))
        
        sm.current = "homing"
        
        self.homed_ok = False
        self.current_user = "Guest"
        
        return sm

if __name__ == "__main__":
    MainApp().run()
