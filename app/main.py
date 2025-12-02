import sys
from PySide6.QtWidgets import QApplication
from app.config import Config

def main():
    """Main entry point for the application."""
    
    # Create Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName("Lab Sheet Generator")
    app.setOrganizationName("University Tools")
    
    # Initialize configuration
    config = Config()
    
    # Check if first run
    if config.is_first_run():
        from app.ui.setup_ui import SetupWindow
        from app.ui.main_ui import MainWindow
        
        setup_window = SetupWindow(config)
        main_window = None  # Will be created after setup
        
        def on_setup_complete(config_data):
            """Called when setup is complete - open main window."""
            nonlocal main_window
            main_window = MainWindow(config)
            main_window.show()
        
        setup_window.setup_complete.connect(on_setup_complete)
        setup_window.show()
    else:
        from app.ui.main_ui import MainWindow
        main_window = MainWindow(config)
        main_window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())