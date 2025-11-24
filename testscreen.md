# MotorControlScreen build_ui() Demo - User Guide

## 📋 Overview

This is the `build_ui()` method extracted from the complete PCR control program's `MotorControlScreen`. All hardware control code has been removed, preserving only the GUI structure. This allows new team members to:

1. **Run independently** - No Raspberry Pi hardware required
2. **Understand layout** - See KivyMD layout structure clearly
3. **Learn components** - Understand various Widget usage
4. **Study animation** - See the pie chart progress animation in action

## 🎯 Key Learning Points

### 1. ProcessFlowWidget - Custom Circular Progress

The core feature is the **pie chart animation** implemented using Kivy's Canvas drawing system.

```
ProcessFlowWidget (Widget)
├── Canvas Drawing
│   ├── Gray Background Circle
│   ├── Blue Progress Sector (0-360°)
│   └── Black Border
├── Properties
│   ├── fill_percentage (0-100)
│   ├── remaining_time (seconds)
│   └── current_stage (0-5)
└── Timer
    └── Clock.schedule_interval(update_timer, 1)
```

### 2. Layout Structure

```
MotorControlScreen (MDScreen)
└── MDBoxLayout (horizontal)
    ├── left_layout (MDFloatLayout, 40%)
    │   ├── Stop Button
    │   ├── Result Button
    │   └── Home Button
    └── right_layout (MDFloatLayout, 60%)
        ├── Temperature Label
        ├── Status Label
        ├── Remaining Time Label
        ├── Date/Time Label
        ├── Logo
        └── ProcessFlowWidget ⭐ (Pie Chart)
```

### 3. Core Concepts

#### 📊 Canvas Drawing

Kivy's Canvas is used for low-level graphics drawing:

```python
with self.canvas:
    # Set color (R, G, B, Alpha)
    Color(0.3, 0.5, 0.9, 1)  # Blue
    
    # Draw circle/ellipse
    Ellipse(
        pos=(x, y),              # Bottom-left corner
        size=(width, height),    # Size
        angle_start=0,           # Start angle (degrees)
        angle_end=180            # End angle (degrees)
    )
    
    # Draw line/border
    Line(
        circle=(center_x, center_y, radius),
        width=2
    )
```

#### 🔄 NumericProperty - Reactive System

NumericProperty automatically triggers updates when values change:

```python
class ProcessFlowWidget(Widget):
    fill_percentage = NumericProperty(0)  # 0-100
    
    def update_canvas(self):
        # Automatically called when fill_percentage changes
        fill_angle = 360 * (self.fill_percentage / 100)
```

#### ⏱️ Clock.schedule_interval - Animation Timer

```python
# Call function every N seconds
Clock.schedule_interval(self.update_timer, 1)  # Every 1 second

def update_timer(self, dt):
    # dt = time interval (required parameter)
    self.remaining_time -= 1
    self.update_canvas()
```

## 🚀 Running the Demo

### Prerequisites

```bash
pip install kivymd
```

### Run Program

```bash
python motorcontrol_buildu_demo.py
```

### Expected Behavior

- Window displays motor control interface
- **Pie chart animates**: Blue sector gradually fills from 0% to 100%
- Real-time updates: Temperature, date/time, remaining time
- Button clicks output to terminal

## 💡 Learning Suggestions

### Step 1: Understand Canvas Drawing

1. Open code, find `update_canvas()` method
2. Study the three drawing steps:
   - Background circle (gray)
   - Progress sector (blue, angle changes)
   - Border (black outline)
3. Run program and observe the animation

### Step 2: Experiment with Modifications

Try modifying these values to see what happens:

```python
# Change colors
Color(1, 0, 0, 1)  # Red instead of blue

# Change progress speed
self.process_flow.fill_percentage += 5  # 5% per second instead of 1%

# Change circle size
size_hint=(0.7, 0.7)  # Larger circle

# Change position
pos_hint={"center_x": 0.3, "center_y": 0.6}  # Move circle
```

### Step 3: Add New Features

Try adding:
- Stage indicator text in the center of circle
- Different colors for different stages
- Pause/Resume button for animation
- Manual progress slider

## 📚 Key Code Sections

### A. ProcessFlowWidget Class

```python
class ProcessFlowWidget(Widget):
    # Reactive properties
    fill_percentage = NumericProperty(0)
    
    def __init__(self, motor_screen, **kwargs):
        super().__init__(**kwargs)
        self.motor_screen = motor_screen
        
        # Start animation timer
        Clock.schedule_interval(self.update_timer, 1)
    
    def update_canvas(self):
        # Core drawing logic
        self.canvas.clear()
        # ... draw circle, sector, border
```

### B. build_ui() Method

```python
def build_ui(self):
    # 1. Create screen and layouts
    screen = MDScreen()
    layout = MDBoxLayout(orientation="horizontal")
    
    # 2. Create buttons and labels
    stop_button = MDButton(...)
    
    # 3. Create ProcessFlowWidget
    self.process_flow = ProcessFlowWidget(self)
    
    # 4. Add to layouts
    self.right_layout.add_widget(self.process_flow)
    
    # 5. Start timers
    Clock.schedule_interval(self.update_date_time, 1)
    
    return screen
```

### C. Simulate Progress

```python
def simulate_progress(self, dt):
    # Increase progress
    if self.process_flow.fill_percentage < 100:
        self.process_flow.fill_percentage += 1
    else:
        self.process_flow.fill_percentage = 0
```

## 🎨 Canvas Drawing Angles

Understanding angle_start and angle_end:

```
        90° (Top)
         |
         |
180° ----+---- 0° (Right)
         |
         |
        270° (Bottom)

Rotation: Counter-clockwise
```

Examples:
- `angle_start=0, angle_end=90` → Right quarter (0° to 90°)
- `angle_start=0, angle_end=180` → Right half (0° to 180°)
- `angle_start=0, angle_end=360` → Full circle

## 🔍 Common Questions

### Q: Why use Canvas instead of KivyMD components?

A: For custom graphics like circular progress bars, Canvas provides precise control over drawing. KivyMD doesn't have a built-in circular progress component, so we create our own using low-level Canvas API.

### Q: Why pass 'self' to ProcessFlowWidget?

A: To allow ProcessFlowWidget to access MotorControlScreen's properties (like status_label). This creates a bidirectional reference:

```python
# In MotorControlScreen.__init__:
self.process_flow = ProcessFlowWidget(self)  # Pass reference

# In ProcessFlowWidget:
self.motor_screen.status_label.text = "..."  # Access parent
```

### Q: What does size_hint=(0.5, 0.5) mean?

A: It means the widget will be 50% of its parent's width and height. If parent is 800x600, this widget will be 400x300.

### Q: Why is dt required in timer callbacks?

A: Kivy's Clock.schedule_interval passes the time interval (dt) to the callback function. Even if you don't use it, you must accept it as a parameter.

## 🎓 Advanced Learning

After completing this demo, you can study:
- **Real temperature control**: TEC module integration
- **Motor control**: TMC2209 stepper motor control
- **Data collection**: ADC reading and CSV export
- **Multi-stage automation**: Step1 → Step2 → Step3 workflow

## 📖 Related Documentation

- [Kivy Canvas Documentation](https://kivy.org/doc/stable/api-kivy.graphics.html)
- [KivyMD Components](https://kivymd.readthedocs.io/)
- [Kivy Properties](https://kivy.org/doc/stable/api-kivy.properties.html)
- [Kivy Clock](https://kivy.org/doc/stable/api-kivy.clock.html)

---

**Created**: 2025-11-24  
**Purpose**: PCR System New Team Member Training - GUI Advanced Topics  
**Original File**: 1117_test_001.py - MotorControlScreen.build_ui() method
