import subprocess


class Settings:
    def __init__(self, model):
        self.invert = False
        self.model = model
        self.view = model.view

    def invert_callback(self):
        self.invert = not self.invert
        self.view.render_menu(self.model.current_menu, invert=self.invert)

    def invert_value_callback(self):
        return "dark" if self.invert else "light"

    def shutdown_callback(self):
        subprocess.call(["sudo", "shutdown", "now"])
