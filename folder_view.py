import os
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.treeview import TreeView, TreeViewLabel
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.button import Button
import threading
from multiprocessing import Pool, Manager

kivy.require('2.0.0')  # Ensure the right Kivy version is being used

class FileExplorer(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = 10

        self.explorer_layout = BoxLayout(orientation='vertical', size_hint=(None, 1), width=300)

        # Create a TreeView to display the file system
        self.treeview = TreeView(hide_root=True, indent_level=4, size_hint=(1, None), height=500)
        self.treeview.bind(on_node_expand=self.on_node_expand)

        # Add a scrollable area to the TreeView
        self.scrollview = ScrollView(size_hint=(None, 1), width=300)
        self.scrollview.add_widget(self.treeview)

        # Create a simple file explorer UI
        self.explorer_layout.add_widget(Label(text="File Explorer", size_hint_y=None, height=40))
        self.explorer_layout.add_widget(self.scrollview)

        # Add the explorer to the main layout
        self.add_widget(self.explorer_layout)
        self.add_widget(Label(text="Editor Content", size_hint=(1, 1)))  # Placeholder for your main editor

        # Start a thread to load the file tree when the app starts
        threading.Thread(target=self.load_file_tree, args=(os.getcwd(),)).start()

    def load_file_tree(self, path):
        """Load the directory structure into the TreeView."""
        # This is called in a separate thread
        with Manager() as manager:
            directories = manager.list()  # Shared list between threads
            with Pool() as pool:
                pool.apply_async(self.fetch_subdirectories, args=(path, directories))
                pool.close()
                pool.join()

            # Schedule UI update on the main thread
            Clock.schedule_once(lambda dt: self.populate_treeview(path, directories))

    def fetch_subdirectories(self, path, directories):
        """Fetch subdirectories and files in a separate process."""
        if not os.path.isdir(path):
            return
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    directories.append((item, item_path))  # Append directory to the shared list
        except PermissionError:
            print(f"Permission denied to access {path}")

    def populate_treeview(self, path, directories):
        """Populate the TreeView with the directories."""
        self.treeview.clear_widgets()
        root_node = self.treeview.add_node(TreeViewLabel(text=path))
        
        # Add directories to the TreeView
        for item, item_path in directories:
            dir_node = self.treeview.add_node(TreeViewLabel(text=item), parent=root_node)
            self.add_subdirectories(item_path, dir_node)

    def add_subdirectories(self, path, parent_node):
        """Add subdirectories and files to the TreeView."""
        threading.Thread(target=self._add_subdirectories_thread, args=(path, parent_node)).start()

    def _add_subdirectories_thread(self, path, parent_node):
        """Add subdirectories recursively in a separate thread."""
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    dir_node = self.treeview.add_node(TreeViewLabel(text=item), parent=parent_node)
                    threading.Thread(target=self.add_subdirectories, args=(item_path, dir_node)).start()
                else:
                    self.treeview.add_node(TreeViewLabel(text=item), parent=parent_node)
        except PermissionError:
            print(f"Permission denied to access {path}")

    def on_node_expand(self, instance, node):
        """Load subdirectories when a directory node is expanded."""
        if isinstance(node, TreeViewLabel):
            text = node.text
            path = os.path.join(os.getcwd(), text)  # Update path based on current working directory
            self.add_subdirectories(path, node)

class FileExplorerApp(App):
    def build(self):
        return FileExplorer()

if __name__ == '__main__':
    FileExplorerApp().run()
