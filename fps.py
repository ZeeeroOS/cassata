import os
import configparser
import cProfile
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.uix.anchorlayout import AnchorLayout

# Define the configuration file path
config_file_path = 'app_config.conf'

class TextInputApp(App):

    def on_start(self):
        self.profile = cProfile.Profile()
        self.profile.enable()

        # Check if the config file exists, if not create it
        if not os.path.exists(config_file_path):
            self.create_default_config()

        # Load the configuration initially
        self.load_config()

        # Schedule a check for config file changes every second
        Clock.schedule_interval(self.check_config_update, 1)

        # Start updating FPS if debug mode is enabled
        if self.debug_mode:
            Clock.schedule_interval(self.update_fps, 1 / 60.0)

    def on_stop(self):
        self.profile.disable()
        self.profile.dump_stats('myapp.profile')

    def build(self):
        # Create the main layout
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Set the background color to the loaded CSS color
        with layout.canvas.before:
            Color(*self.hex_to_rgb(self.bg_color))  # Convert CSS color to RGB
            self.rect = Rectangle(size=layout.size, pos=layout.pos)

        # Update rectangle size and position on resize
        layout.bind(size=self._update_rect, pos=self._update_rect)

        # Create a TextInput widget
        self.text_input = TextInput(
            text='Hello world', height=40, multiline=True
        )
        self.text_input.background_normal = ''  # Remove the background
        self.text_input.background_active = ''  # Remove the active background
        self.text_input.background_color = self.hex_to_rgb(self.bg_color) + (1,)  # RGBA

        # Create the bottom layout for character count
        bottom_layout = BoxLayout(
            orientation="horizontal", size_hint=(1, None), height=40, padding=[10, 5]
        )

        # Add canvas instructions for the gray border
        with bottom_layout.canvas.before:
            Color(0.7, 0.7, 0.7, 1)  # Gray color for the border
            self.border_rect = Rectangle(size=(0, 0), pos=(0, 0))

        bottom_layout.bind(size=self._update_border_rect, pos=self._update_border_rect)

        # Create the character count label
        self.char_count_label = Label(
            text="Characters: 0",
            size_hint=(1, 1),
        )
        bottom_layout.add_widget(self.char_count_label)

        # Bind the text input to update character count
        self.text_input.bind(text=self.update_char_count)

        # Add widgets to the layout
        layout.add_widget(self.text_input)
        layout.add_widget(bottom_layout)

        # Create the FPS label for debug mode
        self.fps_label = Label(
            text="FPS: 0", size_hint=(None, None), size=(100, 30),
            color=(1, 1, 1, 1), halign='left', valign='middle'
        )
        self.fps_label.bind(size=self._update_fps_label_position)

        if self.debug_mode:
            # Anchor the FPS label to the top-left corner
            fps_anchor = AnchorLayout(
                anchor_x='left', anchor_y='top', size_hint=(1, 1)
            )
            fps_anchor.add_widget(self.fps_label)
            layout.add_widget(fps_anchor)

        self.root = layout  # Set the root widget to the layout
        self.update_colors()

        return layout

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

    def _update_border_rect(self, instance, value):
        self.border_rect.size = instance.size
        self.border_rect.pos = instance.pos

    def _update_fps_label_position(self, instance, value):
        self.fps_label.text_size = self.fps_label.size

    def update_char_count(self, instance, value):
        char_count = len(value)
        self.char_count_label.text = f"Characters: {char_count}"

    def update_fps(self, dt):
        """Calculate and display the FPS."""
        fps = Clock.get_rfps()
        self.fps_label.text = f"FPS: {fps:.1f}"

    def create_default_config(self):
        config = configparser.ConfigParser()
        config['Settings'] = {
            'background_color': '#FFFFFF',  # Default white color in CSS hex format
            'debug_mode': 'False',  # Default debug mode is off
        }
        with open(config_file_path, 'w') as configfile:
            config.write(configfile)

    def load_config(self):
        config = configparser.ConfigParser()
        config.read(config_file_path)
        self.bg_color = config.get('Settings', 'background_color', fallback='#FFFFFF')
        self.debug_mode = config.getboolean('Settings', 'debug_mode', fallback=False)

    def update_colors(self):
        if not hasattr(self, 'root'):
            return
        with self.root.canvas.before:
            Color(*self.hex_to_rgb(self.bg_color))
            self.rect = Rectangle(size=self.root.size, pos=self.root.pos)
        self.text_input.background_color = self.hex_to_rgb(self.bg_color) + (1,)
        self.update_text_color()

    def update_text_color(self):
        brightness = self.get_brightness(self.bg_color)
        if brightness < 0.5:
            self.text_input.foreground_color = (1, 1, 1, 1)
            self.char_count_label.color = (1, 1, 1, 1)
        else:
            self.text_input.foreground_color = (0, 0, 0, 1)
            self.char_count_label.color = (0, 0, 0, 1)

    def get_brightness(self, hex_color):
        r, g, b = self.hex_to_rgb(hex_color)
        return (r * 0.299 + g * 0.587 + b * 0.114)

    def check_config_update(self, dt):
        last_modified_time = os.path.getmtime(config_file_path)
        if hasattr(self, 'last_checked_time') and last_modified_time > self.last_checked_time:
            print("Config file updated!")
            self.load_config()
            self.update_colors()
        self.last_checked_time = last_modified_time

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r, g, b = hex_color[0:2], hex_color[2:4], hex_color[4:6]
        elif len(hex_color) == 3:
            r, g, b = hex_color[0] * 2, hex_color[1] * 2, hex_color[2] * 2
        else:
            raise ValueError("Invalid hex color format")
        return (int(r, 16) / 255, int(g, 16) / 255, int(b, 16) / 255)

# Run the app
if __name__ == '__main__':
    TextInputApp().run()
