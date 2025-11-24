# MainScreen Demo - User Guide

## 📋 Overview

This is the `MainScreen` educational version extracted from the complete PCR control program. All hardware control code has been removed, preserving only the GUI structure. This allows new team members to:

1. **Run independently** - No Raspberry Pi hardware required
2. **Understand layout** - See KivyMD layout structure clearly
3. **Learn components** - Understand various Widget usage methods

## 🎯 Key Learning Points

### 1. Layout Structure

```
MainScreen (MDScreen)
└── MDBoxLayout (horizontal) - dual column layout
    ├── left_layout (MDFloatLayout, 40% width)
    │   ├── Report Card (MDCard)
    │   │   └── AnchorLayout
    │   │       └── MDButton (green)
    │   ├── Report Label
    │   ├── Test Card (MDCard)
    │   │   └── AnchorLayout
    │   │       └── MDButton (blue)
    │   └── Test Label
    │
    └── right_layout (MDFloatLayout, 60% width)
        ├── Date Card (MDCard)
        │   └── MDLabel (date)
        ├── Time Card (MDCard)
        │   └── MDLabel (time)
        └── Logo (MDLabel placeholder)
```

### 2. Core Concepts

#### 📦 size_hint - Responsive Sizing
```python
# Relative size (relative to parent component)
size_hint=(0.4, 1)      # Width 40%, Height 100%
size_hint=(None, None)  # Fixed size, not responsive to parent
```

#### 📍 pos_hint - Relative Positioning
```python
# Center
pos_hint={"center_x": 0.5, "center_y": 0.5}

# Top right corner
pos_hint={"right": 1, "top": 1}

# Bottom left
pos_hint={"center_x": 0.25, "y": 0.02}

# 💡 Tip: center_x can exceed 1.0
pos_hint={"center_x": 1.5, "center_y": 0.6}  # Enables multi-card horizontal layout
```

#### 🎨 MDCard - Card Component
```python
MDCard(
    style="elevated",        # Style: elevated (shadow) or outlined (border)
    size_hint=(None, None),  # Fixed size
    size=(dp(200), dp(200)), # Actual dimensions
    radius=[dp(24)],         # Corner radius
    elevation=12,            # Shadow height
    md_bg_color=(1, 1, 1, 1) # Background color RGBA
)
```

#### ⏰ Clock.schedule_interval - Timer Tasks
```python
# Call once per second
Clock.schedule_interval(self.update_time, 1)

def update_time(self, dt):
    # dt is the time interval, must accept this parameter
    now = datetime.now()
    self.time_label.text = now.strftime("%H:%M:%S")
```

### 3. Theme Settings

```python
# Get global theme
self.theme_cls = MDApp.get_running_app().theme_cls

# Set theme style
self.theme_cls.theme_style = "Light"      # or "Dark"
self.theme_cls.primary_palette = "Green"  # Primary color

# Use theme colors
text_color=self.theme_cls.primaryColor
```

## 🚀 Running the Demo

### Prerequisites

```bash
pip install kivymd
```

### Run Program

```bash
python mainscreen_demo.py
```

### Expected Behavior

- Window displays main interface
- Left side: Green Report button + Blue Test button
- Right side: Real-time updated date and time
- Button clicks output to terminal log

## 💡 Learning Suggestions

### Step 1: Understand Layout Hierarchy

1. Open the code and find the `__init__` method
2. Understand layout from outside to inside: MDBoxLayout → FloatLayout → Card → Button
3. Pay attention to each component's `size_hint` and `pos_hint`

### Step 2: Experiment with Modifications

Try modifying these values and observe the changes:

```python
# Change card position
pos_hint={"center_x": 0.3, "center_y": 0.5}

# Change card size
size=(dp(300), dp(300))

# Change button color
md_bg_color=(1, 0, 0, 1)  # Red

# Change corner radius
radius=[dp(50)]  # More rounded
```

### Step 3: Add New Components

Try adding:
- A third function card
- Username display label
- Settings button

## 📚 Related Documentation

- [KivyMD Official Documentation](https://kivymd.readthedocs.io/)
- [Material Design Icons](https://pictogrammers.com/library/mdi/)
- [Kivy Layout Guide](https://kivy.org/doc/stable/gettingstarted/layouts.html)

## 🔍 Common Questions

### Q: Why can center_x in pos_hint exceed 1.0?

A: In FloatLayout, pos_hint values are ratios relative to the parent component. Exceeding 1.0 means the position is outside the parent component's visible area, but if the parent component is in a scrollable or larger layout, these components can still be displayed.

In our example, `left_layout` is 40% width, but cards with `center_x=1.5` can still be displayed because:
- 1.5 × 40% = 60% position (relative to entire screen)
- This actually achieves horizontal arrangement of two cards

### Q: What is dp()?

A: `dp` stands for density-independent pixels. Using `dp()` ensures consistent UI size across different resolution devices.

```python
size=(dp(200), dp(200))  # Recommended
size=(200, 200)          # Not recommended, size varies across devices
```

### Q: Why use AnchorLayout?

A: AnchorLayout is used to center-align components within a container. Using AnchorLayout inside a Card ensures the button stays centered even when changing the Card's size.

## 🎓 Advanced Learning

After completing this demo, you can study other Screens in the project:
- `LockScreen` - User login interface
- `PreTestScreen` - Pre-test preparation interface
- `MotorControlScreen` - Device control interface (hardware-related)
- `ReportScreen` - Report display interface

---

**Created**: 2025-11-24  
**Purpose**: PCR System New Team Member Training - GUI Basics  
**Original File**: MainScreen class from 1117_test_001.py
