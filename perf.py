import os
import configparser
import threading
import cProfile
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock, mainthread
from kivy.uix.anchorlayout import AnchorLayout
from kivy import Config

# Enable GPU acceleration
Config.set('graphics', 'multisamples', '0')
Config.set('graphics', 'stencilbuffer', '1')
Config.set('graphics', 'maxfps', '60')
Config.set('graphics', 'backend', 'sdl2')

# Define the configuration file path
config_file_path = 'app_config.conf'

class TextInputApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = "#FFFFFF"
        self.debug_mode = False
        self.performance_mode = False
        self.stop_threads = False

    def on_start(self):
        self.profile = cProfile.Profile()
        self.profile.enable()

        # Load the configuration in a background thread
        threading.Thread(target=self.load_config_in_background, daemon=True).start()

        # Schedule FPS updates
        Clock.schedule_interval(self.update_fps, 1 / 60.0)

    def on_stop(self):
        self.profile.disable()
        self.profile.dump_stats('myapp.profile')
        self.stop_threads = True

    def build(self):
        # Main layout
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Background color
        with self.layout.canvas.before:
            Color(*self.hex_to_rgb(self.bg_color))
            self.rect = Rectangle(size=self.layout.size, pos=self.layout.pos)
        self.layout.bind(size=self._update_rect, pos=self._update_rect)

        # Text input
        self.text_input = TextInput(
            text="Hello world", height=40, multiline=True,
            background_color=self.hex_to_rgb(self.bg_color) + (1,),
        )
        self.text_input.bind(text=self.update_char_count)

        # Character count label
        self.char_count_label = Label(
            text="Characters: 0", size_hint=(1, None), height=40
        )

        # FPS label (anchored at top-left)
        self.fps_label = Label(
            text="FPS: 0", size_hint=(None, None), size=(100, 30),
            color=(1, 1, 1, 1), halign="left", valign="middle"
        )
        self.fps_anchor = AnchorLayout(
            anchor_x="left", anchor_y="top", size_hint=(1, 1)
        )
        self.fps_anchor.add_widget(self.fps_label)

        # Bottom layout for character count
        self.bottom_layout = BoxLayout(orientation="horizontal", size_hint=(1, None), height=40)
        with self.bottom_layout.canvas.before:
            Color(0.7, 0.7, 0.7, 1)  # Gray border
            self.border_rect = Rectangle(size=(0, 0), pos=(0, 0))
        self.bottom_layout.bind(size=self._update_border_rect, pos=self._update_border_rect)
        self.bottom_layout.add_widget(self.char_count_label)

        # Add elements to the layout
        self.layout.add_widget(self.fps_anchor)
        self.layout.add_widget(self.text_input)
        self.layout.add_widget(self.bottom_layout)

        return self.layout

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

    def _update_border_rect(self, instance, value):
        self.border_rect.size = instance.size
        self.border_rect.pos = instance.pos

    @mainthread
    def update_char_count(self, instance, value):
        self.char_count_label.text = f"Characters: {len(value)}"

    def update_fps(self, dt):
        fps = Clock.get_rfps()
        self.fps_label.text = f"FPS: {fps:.1f}"

        # Toggle visibility based on FPS
        if fps < 10 and not self.performance_mode:
            self.set_visibility(False)
        elif fps >= 10:
            self.set_visibility(True)

    def set_visibility(self, visible):
        opacity = 1 if visible else 0
        self.text_input.opacity = opacity
        self.bottom_layout.opacity = opacity

    def load_config_in_background(self):
        while not self.stop_threads:
            config = configparser.ConfigParser()
            config.read(config_file_path)
            self.bg_color = config.get("Settings", "background_color", fallback="#FFFFFF")
            self.debug_mode = config.getboolean("Settings", "debug_mode", fallback=False)
            self.performance_mode = config.getboolean("Settings", "performance_mode", fallback=False)
            Clock.schedule_once(self.update_colors)
            Clock.schedule_once(self.update_text_color)
            threading.Event().wait(1)  # Check every second

    @mainthread
    def update_colors(self, *args):
        with self.layout.canvas.before:
            Color(*self.hex_to_rgb(self.bg_color))
            self.rect = Rectangle(size=self.layout.size, pos=self.layout.pos)
        self.text_input.background_color = self.hex_to_rgb(self.bg_color) + (1,)

    @mainthread
    def update_text_color(self, *args):
        brightness = self.get_brightness(self.bg_color)
        color = (1, 1, 1, 1) if brightness < 0.5 else (0, 0, 0, 1)
        self.text_input.foreground_color = color
        self.char_count_label.color = color

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip("#")
        if len(hex_color) == 6:
            r, g, b = hex_color[:2], hex_color[2:4], hex_color[4:6]
        elif len(hex_color) == 3:
            r, g, b = hex_color[0] * 2, hex_color[1] * 2, hex_color[2] * 2
        else:
            raise ValueError("Invalid hex color format")
        return tuple(int(x, 16) / 255 for x in (r, g, b))

    def get_brightness(self, hex_color):
        r, g, b = self.hex_to_rgb(hex_color)
        return r * 0.299 + g * 0.587 + b * 0.114

# Run the app
if __name__ == "__main__":
    TextInputApp().run()
