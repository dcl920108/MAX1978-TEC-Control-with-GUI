#!/usr/bin/env python3
"""
MainScreen Standalone Demo - Educational Version
Purpose: Demonstrate KivyMD main interface design pattern

Key Learning Topics:
1. MDBoxLayout - horizontal/vertical layout
2. MDFloatLayout - free positioning layout
3. MDCard - card component usage
4. AnchorLayout - center alignment
5. MDButton - buttons and icons
6. Clock.schedule_interval - timer updates
7. size_hint and pos_hint usage
8. Theme color settings
"""

from kivy.metrics import dp
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText
from kivymd.uix.label import MDLabel
from kivy.uix.anchorlayout import AnchorLayout
from datetime import datetime


class MainScreen(MDScreen):
    """
    Main Interface Screen
    
    Layout Structure:
    - MDBoxLayout (horizontal) - dual column layout
      - Left side (40%): Function card area
      - Right side (60%): Logo and information display area
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # ========== Theme Settings ==========
        # Get global theme object
        self.theme_cls = MDApp.get_running_app().theme_cls
        self.theme_cls.theme_style = "Light"          # Light theme
        self.theme_cls.primary_palette = "Green"      # Primary color: Green
        self.md_bg_color = (1, 1, 1, 1)              # Background: White
        
        # ========== Main Layout ==========
        # Horizontal BoxLayout
        layout = MDBoxLayout(orientation="horizontal")
        
        # Left layout (40% width)
        self.left_layout = MDFloatLayout(size_hint=(0.4, 1))
        
        # Right layout (60% width)
        self.right_layout = MDFloatLayout(size_hint=(0.6, 1))
        
        # ========== Left Side: Report Card ==========
        report_card = MDCard(
            style="elevated",                        # Elevated style (with shadow)
            size_hint=(None, None),                  # Fixed size
            size=(dp(200), dp(200)),                 # 200x200 dp
            radius=[dp(24)],                         # Corner radius
            elevation=12,                            # Shadow height
            pos_hint={"center_x": 0.5, "center_y": 0.6},  # Center, slightly up
        )
        
        # Use AnchorLayout to center the button
        report_anchor = AnchorLayout(
            anchor_x="center",
            anchor_y="center",
            size_hint=(1, 1)
        )
        
        # Report button (green)
        report_btn = MDButton(
            MDButtonIcon(
                icon="file-chart",                   # Material Design icon
                theme_font_size="Custom",
                font_size="64sp",                    # Icon size
                theme_icon_color="Custom",
                icon_color=(1, 1, 1, 1),            # White icon
                pos_hint={"center_x": 0.5, "center_y": 0.5},
            ),
            style="elevated",
            theme_width="Custom",
            height="80dp",
            theme_bg_color="Custom",
            md_bg_color=(0.2, 0.7, 0.3, 1),         # Green background (RGB)
            size_hint=(None, None),
            size=(dp(120), dp(120)),
            on_release=self.on_report_clicked        # Click event
        )
        
        report_anchor.add_widget(report_btn)
        report_card.add_widget(report_anchor)
        self.left_layout.add_widget(report_card)
        
        # Report text label
        report_label = MDLabel(
            text="Report",
            halign="center",
            size_hint=(None, None),
            size=(dp(200), dp(24)),
            pos_hint={"center_x": 0.5, "center_y": 0.33},
            font_style="Title"
        )
        self.left_layout.add_widget(report_label)
        
        # ========== Left Side: Test Card ==========
        test_card = MDCard(
            style="elevated",
            size_hint=(None, None),
            size=(dp(200), dp(200)),
            radius=[dp(24)],
            elevation=12,
            pos_hint={"center_x": 1.5, "center_y": 0.6},  # Position adjusted (note: exceeds 1.0)
        )
        
        test_anchor = AnchorLayout(
            anchor_x="center",
            anchor_y="center",
            size_hint=(1, 1)
        )
        
        # Test button (blue)
        test_btn = MDButton(
            MDButtonIcon(
                icon="dna",                          # DNA icon
                theme_font_size="Custom",
                font_size="64sp",
                theme_icon_color="Custom",
                icon_color=(1, 1, 1, 1),
                pos_hint={"center_x": 0.5, "center_y": 0.5},
            ),
            style="elevated",
            theme_width="Custom",
            height="80dp",
            theme_bg_color="Custom",
            md_bg_color=(0.2, 0.5, 0.9, 1),         # Blue background
            size_hint=(None, None),
            size=(dp(120), dp(120)),
            on_release=self.on_test_clicked
        )
        
        test_anchor.add_widget(test_btn)
        test_card.add_widget(test_anchor)
        self.left_layout.add_widget(test_card)
        
        # Test text label
        test_label = MDLabel(
            text="Test",
            halign="center",
            size_hint=(None, None),
            size=(dp(200), dp(24)),
            pos_hint={"center_x": 1.5, "center_y": 0.33},
            font_style="Title"
        )
        self.left_layout.add_widget(test_label)
        
        # ========== Right Side: Date Card ==========
        self.date_card = MDCard(
            style="elevated",
            size_hint=(None, None),
            size=(dp(140), dp(40)),
            pos_hint={"center_x": 0.25, "y": 0.02},  # Bottom left
            radius=[dp(20)],
            elevation=0,
            md_bg_color=(0.9, 0.9, 0.9, 1),         # Light gray background
        )
        
        # Date label
        self.date_label = MDLabel(
            text="",
            halign="center",
            theme_text_color="Custom",
            text_color=self.theme_cls.primaryColor    # Use theme color
        )
        self.date_card.add_widget(self.date_label)
        self.right_layout.add_widget(self.date_card)
        
        # ========== Right Side: Time Card ==========
        self.time_card = MDCard(
            style="elevated",
            size_hint=(None, None),
            size=(dp(100), dp(40)),
            pos_hint={"center_x": 0.6, "y": 0.02},   # Bottom right
            radius=[dp(20)],
            elevation=0,
            md_bg_color=(0.9, 0.9, 0.9, 1),
        )
        
        # Time label
        self.time_label = MDLabel(
            text="",
            halign="center",
            theme_text_color="Custom",
            text_color=self.theme_cls.primaryColor
        )
        self.time_card.add_widget(self.time_label)
        self.right_layout.add_widget(self.time_card)
        
        # ========== Right Side: Logo Area ==========
        # Use MDLabel instead of FitImage, display [LOGO] placeholder
        logo = MDLabel(
            text="[COMPANY\nLOGO]",
            halign="center",
            font_style="Display",
            size_hint=(None, None),
            size=(dp(233), dp(103)),
            pos_hint={"right": 0.95, "top": 0.98},   # Top right corner
        )
        self.right_layout.add_widget(logo)
        
        # ========== Combine Layouts ==========
        layout.add_widget(self.left_layout)
        layout.add_widget(self.right_layout)
        self.add_widget(layout)
        
        # ========== Timer Update for Time ==========
        # Call update_time method every second
        Clock.schedule_interval(self.update_time, 1)
        # Update immediately once
        self.update_time(0)
    
    def on_report_clicked(self, *args):
        """Report button click event"""
        print("📊 Report button clicked")
        # In real application, would navigate to report page
        # self.manager.current = "report"
    
    def on_test_clicked(self, *args):
        """Test button click event"""
        print("🧬 Test button clicked")
        # In real application, would navigate to test page
        # self.manager.current = "pretest"
    
    def update_time(self, dt):
        """
        Update date and time display
        
        Parameters:
            dt: Time interval passed by Clock (automatically passed, must receive)
        """
        now = datetime.now()
        
        # Format date: Nov 24, 2025
        self.date_label.text = now.strftime("%b %d, %Y")
        
        # Format time: 2:30 PM
        # Note: %-I removes leading zero (Linux/Mac), Windows uses %#I
        try:
            self.time_label.text = now.strftime("%-I:%M %p")
        except ValueError:
            # Windows system uses %#I
            self.time_label.text = now.strftime("%#I:%M %p")


class DemoApp(MDApp):
    """
    Demo Application Main Class
    """
    
    def build(self):
        """Build application"""
        # Create Screen Manager
        sm = MDScreenManager()
        
        # Add MainScreen
        main_screen = MainScreen(name="main")
        sm.add_widget(main_screen)
        
        # Set initial screen
        sm.current = "main"
        
        return sm
    
    def on_start(self):
        """Callback when application starts"""
        print("\n" + "="*60)
        print("🎓 MainScreen Educational Demo Program")
        print("="*60)
        print("\n📚 Key Learning Points:")
        print("  1. MDBoxLayout horizontal layout - left/right columns")
        print("  2. MDFloatLayout - free positioning with pos_hint")
        print("  3. MDCard component - rounded corners, shadows, styles")
        print("  4. AnchorLayout - component centering")
        print("  5. MDButton + MDButtonIcon - buttons and icons")
        print("  6. Clock.schedule_interval - timer updates")
        print("  7. size_hint and pos_hint - responsive layout")
        print("  8. Theme settings - theme_cls global theme")
        print("\n💡 Layout Description:")
        print("  - Left 40%: Function card area (Report and Test)")
        print("  - Right 60%: Info display area (Logo, date, time)")
        print("  - pos_hint center_x values can exceed 1.0 for multi-card layout")
        print("\n🎨 Style Tips:")
        print("  - Report card: Green (0.2, 0.7, 0.3)")
        print("  - Test card: Blue (0.2, 0.5, 0.9)")
        print("  - Date/Time cards: Light gray background")
        print("="*60 + "\n")


if __name__ == "__main__":
    DemoApp().run()
