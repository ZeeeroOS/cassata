import os
import configparser
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

config_file_path = 'app_config.conf'

class TextInputApp(App):
    def on_start(self):
        # Check if the config file exists, if not create it
        if not os.path.exists(config_file_path):
            self.create_default_config()
        
        # Load the configuration initially
        self.load_config()

        # Schedule a check for config file changes at a reduced interval
        Clock.schedule_interval(self.check_config_update, 5)

    def on_stop(self):
        self.profile.disable()
        self.profile.dump_stats('myapp.profile')

    def build(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Set the background color to the loaded CSS color
        with layout.canvas.before:
            Color(*self.hex_to_rgb(self.bg_color))  # Convert CSS color to RGB
            self.rect = Rectangle(size=layout.size, pos=layout.pos)
        
        # Bind resize to _update_rect to avoid redundant canvas updates
        layout.bind(size=self._update_rect, pos=self._update_rect)

        self.text_input = TextInput(text='Hello world', height=40, multiline=True)
        self.text_input.background_normal = ''  # Remove the background
        self.text_input.background_active = ''   # Remove the active background
        self.text_input.background_color = self.hex_to_rgb(self.bg_color) + (1,)  # RGBA

        layout.add_widget(self.text_input)
        self.root = layout  # Set the root widget to the layout

        self.update_colors()

        return layout

    def _update_rect(self, instance, value):
        # Only update the size and position of the existing rectangle
        self.rect.size = instance.size
        self.rect.pos = instance.pos
        self.root.canvas.ask_update()  # Only request canvas update if necessary

    def create_default_config(self):
        config = configparser.ConfigParser()
        config['Settings'] = {
            'background_color': '#FFFFFF',  # Default white color in CSS hex format
        }
        with open(config_file_path, 'w') as configfile:
            config.write(configfile)

    def load_config(self):
        config = configparser.ConfigParser()
        config.read(config_file_path)
        self.bg_color = config.get('Settings', 'background_color', fallback='#FFFFFF')

    def update_colors(self):
        """Update the app and TextInput background color dynamically."""
        if not hasattr(self, 'root'):
            return

        # Only update if the background color has changed
        if hasattr(self, 'last_bg_color') and self.last_bg_color != self.bg_color:
            with self.root.canvas.before:
                Color(*self.hex_to_rgb(self.bg_color))  # Convert CSS color to RGB
                self.rect = Rectangle(size=self.root.size, pos=self.root.pos)
            self.text_input.background_color = self.hex_to_rgb(self.bg_color) + (1,)
            self.update_text_color()

            self.last_bg_color = self.bg_color

    def update_text_color(self):
        brightness = self.get_brightness(self.bg_color)
        if brightness < 0.5:
            self.text_input.foreground_color = (1, 1, 1, 1)  # White text
        else:
            self.text_input.foreground_color = (0, 0, 0, 1)  # Black text

    def get_brightness(self, hex_color):
        r, g, b = self.hex_to_rgb(hex_color)
        return (r * 0.299 + g * 0.587 + b * 0.114)

    def check_config_update(self, dt):
        last_modified_time = os.path.getmtime(config_file_path)
        if hasattr(self, 'last_checked_time'):
            if last_modified_time > self.last_checked_time:
                self.load_config()
                self.update_colors()
        self.last_checked_time = last_modified_time

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r, g, b = hex_color[0:2], hex_color[2:4], hex_color[4:6]
        elif len(hex_color) == 3:
            r, g, b = hex_color[0]*2, hex_color[1]*2, hex_color[2]*2
        else:
            raise ValueError("Invalid hex color format")
        return (int(r, 16)/255, int(g, 16)/255, int(b, 16)/255)

if __name__ == '__main__':
    TextInputApp().run()
