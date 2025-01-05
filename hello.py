import os
import configparser
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
import cProfile
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

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

        # Create a TextInput widget with a transparent background
        self.text_input = TextInput(text='Hello world', height=40, multiline=True)
        self.text_input.background_normal = ''  # Remove the background
        self.text_input.background_active = ''   # Remove the active background
        # Set the background color of the TextInput to match the app's background
        self.text_input.background_color = self.hex_to_rgb(self.bg_color) + (1,)  # RGBA

        # Create a Label to display the input text
        # self.label = Label(text='Your text will appear here', size_hint=(1, 0.2))

        # Create a Button to update the label with text input
        #button = Button(text='Submit', size_hint=(1, 0.2))
        #button.bind(on_press=self.update_label)

        # Add widgets to the layout
        layout.add_widget(self.text_input)
        #layout.add_widget(button)
        #layout.add_widget(self.label)

        self.root = layout  # Set the root widget to the layout

        # Call update_colors after root is initialized
        self.update_colors()
        self.title = 'Cassata'
        self.icon = './assets/images/Cassata.ico'
        # Call update_text_color after label is created
        self.update_text_color()

        return layout

    def _update_rect(self, instance, value):
        # Update the rectangle size and position whenever the window is resized
        self.rect.size = instance.size
        self.rect.pos = instance.pos

    def update_label(self, instance):
        # Update the label with the text from the TextInput
        #self.label.text = self.text_input.text
        print()

    def create_default_config(self):
        # Create a config parser and add default values (using CSS hex color)
        config = configparser.ConfigParser()
        config['Settings'] = {
            'background_color': '#FFFFFF',  # Default white color in CSS hex format
        }
        
        # Write the config to a file
        with open(config_file_path, 'w') as configfile:
            config.write(configfile)

    def load_config(self):
        # Load the configuration from the .conf file
        config = configparser.ConfigParser()
        config.read(config_file_path)
        
        # Read background color from config file (default is white if not found)
        self.bg_color = config.get('Settings', 'background_color', fallback='#FFFFFF')

    def update_colors(self):
        """Update the app and TextInput background color dynamically."""
        if not hasattr(self, 'root'):
            return  # Ensure root is set before updating

        # Update the app background color
        with self.root.canvas.before:
            Color(*self.hex_to_rgb(self.bg_color))  # Convert CSS color to RGB
            self.rect = Rectangle(size=self.root.size, pos=self.root.pos)
        
        # Update the TextInput background color
        self.text_input.background_color = self.hex_to_rgb(self.bg_color) + (1,)  # RGBA
        
        # Request the canvas to be updated
        self.root.canvas.ask_update()

        # Update text color based on background color brightness
        self.update_text_color()

    def update_text_color(self):
        """Update the text color dynamically based on the background brightness."""
        brightness = self.get_brightness(self.bg_color)
        
        # If brightness is less than 0.5 (dark background), use light text color
        if brightness < 0.5:
            self.text_input.foreground_color = (1, 1, 1, 1)  # White text
            #self.label.color = (1, 1, 1, 1)  # White text for label as well
        else:
            self.text_input.foreground_color = (0, 0, 0, 1)  # Black text
            #self.label.color = (0, 0, 0, 1)  # Black text for label as well

    def get_brightness(self, hex_color):
        """Calculate the brightness of a hex color. Returns a value between 0 (dark) and 1 (bright)."""
        r, g, b = self.hex_to_rgb(hex_color)
        # Formula to calculate brightness
        brightness = (r * 0.299 + g * 0.587 + b * 0.114)
        return brightness

    def check_config_update(self, dt):
        """Check if the config file has been updated and reload if necessary."""
        # Check if the file's last modified time has changed
        last_modified_time = os.path.getmtime(config_file_path)

        if hasattr(self, 'last_checked_time'):
            if last_modified_time > self.last_checked_time:
                print("Config file updated!")
                self.load_config()
                self.update_colors()  # Trigger color update after config change

        # Update the last checked time
        self.last_checked_time = last_modified_time

    def hex_to_rgb(self, hex_color):
        """Convert a hex color string to an RGB tuple."""
        hex_color = hex_color.lstrip('#')  # Remove the leading '#'
        if len(hex_color) == 6:  # Standard 6-character hex format
            r, g, b = hex_color[0:2], hex_color[2:4], hex_color[4:6]
        elif len(hex_color) == 3:  # Shortened 3-character hex format
            r, g, b = hex_color[0]*2, hex_color[1]*2, hex_color[2]*2
        else:
            raise ValueError("Invalid hex color format")
        
        # Convert to RGB values (0-1)
        return (int(r, 16)/255, int(g, 16)/255, int(b, 16)/255)

# Run the app
if __name__ == '__main__':
    TextInputApp().run()

