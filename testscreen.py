#!/usr/bin/env python3
"""
MotorControlScreen build_ui() Standalone Demo - Educational Version
Focus: Pie Chart Progress Animation (ProcessFlowWidget)

Key Learning Topics:
1. Custom Widget - inherit from kivy.uix.widget.Widget
2. Canvas Drawing - using Kivy Graphics instructions
3. NumericProperty - Kivy's reactive properties
4. Clock.schedule_interval - animation timer updates
5. Circular Progress Bar - Ellipse with angle_start and angle_end
"""

from kivy.metrics import dp
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Line
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText
from kivymd.uix.label import MDLabel
from datetime import datetime
import math


class ProcessFlowWidget(Widget):
    """
    Pie Chart Progress Animation Widget
    
    Core Concepts:
    - Use Canvas to draw circles and sectors
    - fill_percentage controls progress (0-100)
    - Auto-update animation
    """
    
    # Kivy reactive properties - auto-trigger updates when values change
    remaining_time = NumericProperty(10)              # Remaining time (seconds)
    current_stage = NumericProperty(0)                # Current stage index
    fill_percentage = NumericProperty(0)               # Fill percentage 0-100
    stage_text = StringProperty("Initializing")        # Stage text
    total_time_per_stage = 10                          # Duration per stage (seconds)
    
    def __init__(self, motor_screen, **kwargs):
        super().__init__(**kwargs)
        
        # Save reference to MotorControlScreen (for updating status)
        self.motor_screen = motor_screen
        
        # Define all stages
        self.stages = [
            "Preheating",           # Preheating stage
            "Heating",              # Heating stage
            "Holding",              # High temperature holding stage
            "Cooling",              # Cooling stage
            "PCR Cycling",          # PCR data collection cycles
            "Experiment Complete"   # Experiment finished
        ]
        
        print(f"📋 ProcessFlowWidget initialized with {len(self.stages)} stages")
        
        # Start timer - update every second
        Clock.schedule_interval(self.update_timer, 1)
        
        # Initial draw
        self.update_canvas()
    
    def update_timer(self, dt):
        """
        Timer callback - called every second
        
        Functions:
        1. Update remaining time
        2. Switch stages
        3. Update progress percentage
        """
        if self.remaining_time > 0:
            self.remaining_time -= 1
        else:
            # Time's up, switch to next stage
            self.current_stage = (self.current_stage + 1) % len(self.stages)
            self.stage_text = self.stages[self.current_stage]
            self.remaining_time = self.total_time_per_stage
        
        # Update canvas
        self.update_canvas()
    
    def on_size(self, *args):
        """Redraw when window size changes"""
        self.update_canvas()
    
    def update_canvas(self):
        """
        Core drawing method - draw pie chart progress animation
        
        Drawing steps:
        1. Clear canvas
        2. Draw gray background circle
        3. Draw blue progress sector
        4. Draw black border
        """
        # Clear previous drawings
        self.canvas.clear()
        
        # Calculate circle radius and center position
        radius = min(self.width, self.height) / 2 - 20
        center_x, center_y = self.center_x, self.center_y
        
        with self.canvas:
            # ========== 1. Draw gray background circle ==========
            Color(0.9, 0.9, 0.9, 1)  # Light gray (R, G, B, Alpha)
            Ellipse(
                pos=(center_x - radius, center_y - radius),  # Bottom-left position
                size=(radius * 2, radius * 2)                # Circle size
            )
            
            # ========== 2. Draw blue progress sector ==========
            # Calculate fill angle based on fill_percentage
            fill_angle = 360 * (self.fill_percentage / 100)
            Color(0.3, 0.5, 0.9, 1)  # Blue
            Ellipse(
                pos=(center_x - radius, center_y - radius),
                size=(radius * 2, radius * 2),
                angle_start=0,           # Start angle (from right, counter-clockwise)
                angle_end=fill_angle     # End angle
            )
            
            # ========== 3. Draw black border ==========
            Color(0, 0, 0, 1)  # Black
            Line(
                circle=(center_x, center_y, radius),  # (center_x, center_y, radius)
                width=2                                # Line width
            )


class MotorControlScreen(MDScreen):
    """
    Motor Control Screen - Educational Version
    
    Main Features:
    1. build_ui() layout structure
    2. ProcessFlowWidget pie chart animation integration
    3. Timer-based time display updates
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize variables
        self.project_name = ""
        self.stop_requested = False
        
        # ========== Create pie chart animation widget ==========
        # Pass 'self' so ProcessFlowWidget can access this Screen
        self.process_flow = ProcessFlowWidget(
            self,
            size_hint=(0.5, 0.5),                      # 50% of parent width/height
            pos_hint={"center_x": 0.5, "center_y": 0.5}  # Centered
        )
        
        # ========== Project name label ==========
        self.project_label = MDLabel(
            text="Project: Demo Project",
            halign="center",
            pos_hint={"center_x": 0.5, "center_y": 0.05},
        )
        
        # ========== Remaining time label ==========
        self.remaining_time_label = MDLabel(
            text="Remaining: 10:00",  # Default: 10 minutes
            font_style="Title",
            halign="center",
            pos_hint={"center_x": 0.2, "center_y": 0.9},
        )
        
        # Call build_ui() to construct the interface
        ui = self.build_ui()
        self.add_widget(ui)
        self.add_widget(self.project_label)
    
    def build_ui(self):
        """
        Build user interface
        
        Layout Structure:
        MDScreen
        └── MDBoxLayout (horizontal)
            ├── left_layout (MDFloatLayout, 40% width)
            │   ├── Stop Button
            │   ├── Result Button
            │   └── Home Button
            └── right_layout (MDFloatLayout, 60% width)
                ├── Temperature Label
                ├── Status Label
                ├── Remaining Time Label
                ├── Date/Time Label
                ├── Logo
                └── ProcessFlowWidget (Pie Chart Animation)
        """
        
        # Set theme
        self.theme_cls = MDApp.get_running_app().theme_cls
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Green"
        
        # Create main screen
        screen = MDScreen(md_bg_color=(1, 1, 1, 1))
        
        # Main horizontal layout
        layout = MDBoxLayout(orientation="horizontal")
        self.left_layout = MDFloatLayout(size_hint=(0.4, 1))
        self.right_layout = MDFloatLayout(size_hint=(0.6, 1))
        
        # ========== Left side: Control buttons ==========
        
        # Home button (top right)
        self.back_button = MDButton(
            MDButtonIcon(icon="home"),
            MDButtonText(text="Home", font_style="Title"),
            style="elevated",
            pos_hint={"center_x": 2.2, "center_y": 0.95},
            size_hint=(0.25, 0.1),
            on_release=self.on_home_clicked
        )
        
        # Back button (top left)
        self.back_02_button = MDButton(
            MDButtonIcon(icon="arrow-left"),
            MDButtonText(text="Back", font_style="Title"),
            style="elevated",
            size_hint=(None, None),
            size=(dp(100), dp(40)),
            pos_hint={"x": 0.02, "top": 0.98},
            on_release=self.on_back_clicked
        )
        screen.add_widget(self.back_02_button)
        
        # Stop button
        stop_button = MDButton(
            MDButtonIcon(icon="timer-cancel"),
            MDButtonText(text="  Stop  ", font_style="Title"),
            style="elevated",
            pos_hint={"center_x": 0.5, "center_y": 0.65},
            height="56dp",
            size_hint_x=0.6,
            on_press=self.on_stop_clicked
        )
        
        # Result button
        self.result_button = MDButton(
            MDButtonIcon(icon="folder"),
            MDButtonText(text="Result", font_style="Title"),
            style="elevated",
            pos_hint={"center_x": 0.5, "center_y": 0.4},
            height="56dp",
            size_hint_x=0.6,
            on_release=self.on_result_clicked
        )
        
        # ========== Right side: Status display ==========
        
        # Current temperature label
        self.actual_temperature_label = MDLabel(
            text="Current Temperature: -- °C",
            halign="center",
            pos_hint={"center_x": -0.4, "center_y": 0.1},
        )
        
        # Status label
        self.status_label = MDLabel(
            text="Status: Ready",
            halign="center",
            pos_hint={"center_x": 0.2, "center_y": 0.8},
        )
        
        # Date/time label
        self.date_time_label = MDLabel(
            text="YYYY-MM-DD HH:MM:SS",
            halign="left",
            size_hint=(None, None),
            size=(dp(200), dp(40)),
            pos_hint={"x": -0.6, "y": 0},
        )
        
        # Logo placeholder
        logo = MDLabel(
            text="[LOGO]",
            halign="center",
            font_style="Display",
            size_hint=(None, None),
            size=(dp(233), dp(103)),
            pos_hint={"right": 1.1, "top": 0.98},
        )
        
        # ========== Add widgets to layouts ==========
        
        # Left layout
        self.left_layout.add_widget(stop_button)
        self.left_layout.add_widget(self.result_button)
        self.left_layout.add_widget(self.back_button)
        
        # Right layout
        self.right_layout.add_widget(self.actual_temperature_label)
        self.right_layout.add_widget(self.status_label)
        self.right_layout.add_widget(self.remaining_time_label)
        self.right_layout.add_widget(self.date_time_label)
        self.right_layout.add_widget(logo)
        self.right_layout.add_widget(self.process_flow)  # Add pie chart animation
        
        # Combine left and right layouts
        layout.add_widget(self.left_layout)
        layout.add_widget(self.right_layout)
        screen.add_widget(layout)
        
        # ========== Start timers ==========
        
        # Update temperature every 0.5 seconds
        Clock.schedule_interval(self.update_actual_temperature, 0.5)
        
        # Update date/time every second
        Clock.schedule_interval(self.update_date_time, 1)
        
        # Simulate progress update
        Clock.schedule_interval(self.simulate_progress, 1)
        
        return screen
    
    def update_actual_temperature(self, dt):
        """
        Update temperature display
        
        In real application, this would read from actual sensor
        Here we just simulate with random values
        """
        import random
        temp = 25 + random.random() * 10  # Simulate 25-35°C
        self.actual_temperature_label.text = f"Current Temperature: {temp:.1f} °C"
    
    def update_date_time(self, dt):
        """Update date/time display"""
        now = datetime.now()
        self.date_time_label.text = now.strftime("%Y-%m-%d %H:%M:%S")
    
    def simulate_progress(self, dt):
        """
        Simulate progress for demo purposes
        In real application, this would be updated by actual process
        """
        # Increase progress by 1% each second
        if self.process_flow.fill_percentage < 100:
            self.process_flow.fill_percentage += 1
        else:
            # Reset to 0 when reaching 100%
            self.process_flow.fill_percentage = 0
        
        # Update remaining time display
        total_seconds = int(self.process_flow.remaining_time)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        self.remaining_time_label.text = f"Remaining: {minutes:02d}:{seconds:02d}"
    
    # ========== Button event handlers ==========
    
    def on_home_clicked(self, *args):
        """Home button clicked"""
        print("🏠 Home button clicked")
    
    def on_back_clicked(self, *args):
        """Back button clicked"""
        print("⬅️  Back button clicked")
    
    def on_stop_clicked(self, *args):
        """Stop button clicked"""
        print("⏹️  Stop button clicked")
        self.stop_requested = True
    
    def on_result_clicked(self, *args):
        """Result button clicked"""
        print("📁 Result button clicked")


class DemoApp(MDApp):
    """Demo Application Main Class"""
    
    def build(self):
        """Build application"""
        # Create Screen Manager
        sm = MDScreenManager()
        
        # Add MotorControlScreen
        motor_screen = MotorControlScreen(name="motor")
        sm.add_widget(motor_screen)
        
        # Set initial screen
        sm.current = "motor"
        
        return sm
    
    def on_start(self):
        """Callback when application starts"""
        print("\n" + "="*70)
        print("🎓 MotorControlScreen build_ui() Demo")
        print("="*70)
        print("\n📚 Key Learning Points:")
        print("  1. ProcessFlowWidget - Custom circular progress widget")
        print("  2. Canvas Drawing - Using Color, Ellipse, Line")
        print("  3. NumericProperty - Reactive property system")
        print("  4. Clock.schedule_interval - Timer-based animations")
        print("  5. Complex Layout - Dual-column with multiple components")
        print("\n💡 Animation Features:")
        print("  - Pie chart fills from 0% to 100%")
        print("  - Automatic stage switching")
        print("  - Real-time updates")
        print("\n🎨 Canvas Drawing Concepts:")
        print("  - Background circle: Gray base")
        print("  - Progress sector: Blue fill (angle_start to angle_end)")
        print("  - Border: Black outline")
        print("\n🔧 Try modifying:")
        print("  - Change fill_percentage increment speed")
        print("  - Modify colors in update_canvas()")
        print("  - Add more stages to self.stages list")
        print("="*70 + "\n")


if __name__ == "__main__":
    DemoApp().run()
