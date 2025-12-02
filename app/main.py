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
        setup_window = SetupWindow(config)
        
        def on_setup_complete(config_data):
            """Called when setup is complete."""
            # TODO: Open main window after setup
            print("Setup completed successfully!")
            app.quit()
        
        setup_window.setup_complete.connect(on_setup_complete)
        setup_window.show()
    else:
        print("Configuration found - showing main window")
        # TODO: Show main UI
        # from app.ui.main_ui import MainWindow
        # main_window = MainWindow(config)
        # main_window.show()
        
        # For now, just show loaded config
        loaded_config = config.load_config()
        print(f"Loaded config: {loaded_config}")
        return 0
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())