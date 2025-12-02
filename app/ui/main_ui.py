from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QSpinBox, QMessageBox, QGroupBox,
    QFormLayout, QFileDialog, QMenu
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QAction, QPixmap
from app.generator import generate_lab_sheet
from app.utils.paths import get_output_dir
import os


class GeneratorThread(QThread):
    """Thread for generating lab sheets without blocking UI."""
    
    finished = Signal(str)  # Emits the output file path
    error = Signal(str)  # Emits error message
    
    def __init__(self, student_name, student_id, module_name, module_code, 
                 practical_number, logo_path, output_dir):
        super().__init__()
        self.student_name = student_name
        self.student_id = student_id
        self.module_name = module_name
        self.module_code = module_code
        self.practical_number = practical_number
        self.logo_path = logo_path
        self.output_dir = output_dir
    
    def run(self):
        """Generate the lab sheet."""
        try:
            # Generate in the output directory
            original_dir = os.getcwd()
            os.chdir(self.output_dir)
            
            output_file = generate_lab_sheet(
                student_name=self.student_name,
                student_id=self.student_id,
                module_name=self.module_name,
                module_code=self.module_code,
                practical_number=self.practical_number,
                logo_path=str(self.logo_path)
            )
            
            os.chdir(original_dir)
            
            # Return full path
            full_path = os.path.join(self.output_dir, output_file)
            self.finished.emit(full_path)
            
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window for generating lab sheets."""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.config_data = config.load_config()
        self.output_dir = get_output_dir()
        self.generator_thread = None
        
        self.setWindowTitle("Lab Sheet Generator")
        self.setMinimumSize(700, 550)
        
        self.init_ui()
        self.init_menu()
    
    def init_menu(self):
        """Initialize menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        open_output_action = QAction("Open Output Folder", self)
        open_output_action.triggered.connect(self.open_output_folder)
        file_menu.addAction(open_output_action)
        
        change_output_action = QAction("Change Output Folder", self)
        change_output_action.triggered.connect(self.change_output_folder)
        file_menu.addAction(change_output_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Settings menu
        settings_menu = menubar.addMenu("Settings")
        
        edit_config_action = QAction("Edit Configuration", self)
        edit_config_action.triggered.connect(self.edit_configuration)
        settings_menu.addAction(edit_config_action)
        
        reset_config_action = QAction("Reset Configuration", self)
        reset_config_action.triggered.connect(self.reset_configuration)
        settings_menu.addAction(reset_config_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def init_ui(self):
        """Initialize the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        
        # Header
        header = QLabel("Generate Lab Sheet")
        header.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            color: #156082;
            margin: 10px;
        """)
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)
        
        # Student Info Display
        info_group = QGroupBox("Your Information")
        info_layout = QVBoxLayout()
        
        self.student_info_label = QLabel()
        self.student_info_label.setStyleSheet("font-size: 13px; padding: 5px;")
        self.update_student_info_display()
        info_layout.addWidget(self.student_info_label)
        
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)
        
        # Logo Status
        logo_group = QGroupBox("University Logo")
        logo_layout = QHBoxLayout()
        
        self.logo_preview = QLabel()
        self.logo_preview.setFixedSize(88, 84)
        self.logo_preview.setStyleSheet("border: 1px solid #ccc; background: #f5f5f5;")
        self.logo_preview.setAlignment(Qt.AlignCenter)
        
        logo_path = self.config.get_logo_path()
        if logo_path and logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            scaled_pixmap = pixmap.scaled(88, 84, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_preview.setPixmap(scaled_pixmap)
            self.logo_status_label = QLabel("✓ Logo loaded")
            self.logo_status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.logo_preview.setText("No Logo")
            self.logo_status_label = QLabel("⚠ No logo set")
            self.logo_status_label.setStyleSheet("color: orange; font-weight: bold;")
        
        logo_layout.addWidget(self.logo_preview)
        logo_layout.addWidget(self.logo_status_label)
        logo_layout.addStretch()
        
        logo_group.setLayout(logo_layout)
        main_layout.addWidget(logo_group)
        
        # Generator Section
        generator_group = QGroupBox("Generate Lab Sheet")
        generator_layout = QFormLayout()
        generator_layout.setSpacing(15)
        
        # Module selection
        self.module_combo = QComboBox()
        generator_layout.addRow("Select Module:", self.module_combo)
        
        # Practical number
        self.practical_spin = QSpinBox()
        self.practical_spin.setMinimum(1)
        self.practical_spin.setMaximum(99)
        self.practical_spin.setValue(1)
        self.practical_spin.setPrefix("Practical ")
        generator_layout.addRow("Practical Number:", self.practical_spin)
        
        generator_group.setLayout(generator_layout)
        main_layout.addWidget(generator_group)
        
        # Output directory display
        output_info = QLabel(f"Output folder: {self.output_dir}")
        output_info.setStyleSheet("color: gray; font-size: 11px; font-style: italic;")
        output_info.setWordWrap(True)
        main_layout.addWidget(output_info)
        
        # Generate button
        main_layout.addStretch()
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.generate_btn = QPushButton("Generate Lab Sheet")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #156082;
                color: white;
                padding: 12px 30px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #1a7599;
            }
            QPushButton:pressed {
                background-color: #124d66;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_lab_sheet)
        button_layout.addWidget(self.generate_btn)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 12px; padding: 10px;")
        main_layout.addWidget(self.status_label)
        
        central_widget.setLayout(main_layout)
        
        # Populate modules after all UI elements are created
        self.populate_modules()
    
    def update_student_info_display(self):
        """Update the student information display."""
        name = self.config_data.get('student_name', 'N/A')
        student_id = self.config_data.get('student_id', 'N/A')
        modules_count = len(self.config_data.get('modules', []))
        
        info_text = f"<b>Name:</b> {name}<br><b>Student ID:</b> {student_id}<br><b>Modules:</b> {modules_count} module(s)"
        self.student_info_label.setText(info_text)
    
    def populate_modules(self):
        """Populate the module dropdown."""
        self.module_combo.clear()
        modules = self.config_data.get('modules', [])
        
        if not modules:
            self.module_combo.addItem("No modules configured")
            self.generate_btn.setEnabled(False)
        else:
            for module in modules:
                display_text = f"{module['name']} ({module['code']})"
                self.module_combo.addItem(display_text, module)
            self.generate_btn.setEnabled(True)
    
    def generate_lab_sheet(self):
        """Generate the lab sheet document."""
        # Check if modules exist
        if self.module_combo.count() == 0 or self.module_combo.currentData() is None:
            QMessageBox.warning(
                self,
                "No Modules",
                "Please add modules in the configuration first."
            )
            return
        
        # Get selected module
        module = self.module_combo.currentData()
        practical_num = self.practical_spin.value()
        
        # Get logo path
        logo_path = self.config.get_logo_path()
        if not logo_path or not logo_path.exists():
            reply = QMessageBox.question(
                self,
                "No Logo",
                "No logo is configured. Generate without logo?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
            # Use a placeholder or handle no logo case
            logo_path = None
        
        # Disable button and show status
        self.generate_btn.setEnabled(False)
        self.status_label.setText("Generating lab sheet...")
        self.status_label.setStyleSheet("color: #156082; font-size: 12px; padding: 10px;")
        
        # Create and start generator thread
        self.generator_thread = GeneratorThread(
            student_name=self.config_data['student_name'],
            student_id=self.config_data['student_id'],
            module_name=module['name'],
            module_code=module['code'],
            practical_number=f"Practical {practical_num:02d}",
            logo_path=logo_path,
            output_dir=self.output_dir
        )
        
        self.generator_thread.finished.connect(self.on_generation_complete)
        self.generator_thread.error.connect(self.on_generation_error)
        self.generator_thread.start()
    
    def on_generation_complete(self, file_path):
        """Called when generation is complete."""
        self.generate_btn.setEnabled(True)
        self.status_label.setText(f"✓ Lab sheet generated successfully!")
        self.status_label.setStyleSheet("color: green; font-weight: bold; font-size: 12px; padding: 10px;")
        
        # Show success dialog
        reply = QMessageBox.information(
            self,
            "Success",
            f"Lab sheet generated successfully!\n\nSaved to:\n{file_path}\n\nWould you like to open the folder?",
            QMessageBox.Open | QMessageBox.Close
        )
        
        if reply == QMessageBox.Open:
            self.open_output_folder()
    
    def on_generation_error(self, error_msg):
        """Called when generation fails."""
        self.generate_btn.setEnabled(True)
        self.status_label.setText("✗ Generation failed")
        self.status_label.setStyleSheet("color: red; font-weight: bold; font-size: 12px; padding: 10px;")
        
        QMessageBox.critical(
            self,
            "Error",
            f"Failed to generate lab sheet:\n\n{error_msg}"
        )
    
    def open_output_folder(self):
        """Open the output folder in file explorer."""
        if os.name == 'nt':  # Windows
            os.startfile(self.output_dir)
        elif os.name == 'posix':  # macOS/Linux
            os.system(f'open "{self.output_dir}"' if os.uname().sysname == 'Darwin' 
                     else f'xdg-open "{self.output_dir}"')
    
    def change_output_folder(self):
        """Change the output folder."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            str(self.output_dir)
        )
        
        if folder:
            self.output_dir = folder
            QMessageBox.information(
                self,
                "Output Folder Changed",
                f"Lab sheets will now be saved to:\n{folder}"
            )
    
    def edit_configuration(self):
        """Open setup wizard to edit configuration."""
        from app.ui.setup_ui import SetupWindow
        
        setup_window = SetupWindow(self.config)
        
        # Pre-fill with existing data
        setup_window.name_input.setText(self.config_data.get('student_name', ''))
        setup_window.id_input.setText(self.config_data.get('student_id', ''))
        
        # Pre-fill modules
        setup_window.modules = self.config_data.get('modules', []).copy()
        for module in setup_window.modules:
            setup_window.module_list.addItem(f"{module['name']} - {module['code']}")
        
        # Pre-fill logo
        logo_path = self.config.get_logo_path()
        if logo_path and logo_path.exists():
            setup_window.logo_path = str(logo_path)
            setup_window.logo_label.setText(logo_path.name)
            setup_window.logo_label.setStyleSheet("color: green;")
            pixmap = QPixmap(str(logo_path))
            scaled_pixmap = pixmap.scaled(110, 105, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            setup_window.logo_preview.setPixmap(scaled_pixmap)
        
        def on_setup_complete(config_data):
            # Reload config
            self.config_data = self.config.load_config()
            self.update_student_info_display()
            self.populate_modules()
            
            # Update logo preview
            logo_path = self.config.get_logo_path()
            if logo_path and logo_path.exists():
                pixmap = QPixmap(str(logo_path))
                scaled_pixmap = pixmap.scaled(88, 84, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.logo_preview.setPixmap(scaled_pixmap)
                self.logo_status_label.setText("✓ Logo loaded")
                self.logo_status_label.setStyleSheet("color: green; font-weight: bold;")
        
        setup_window.setup_complete.connect(on_setup_complete)
        setup_window.show()
    
    def reset_configuration(self):
        """Reset all configuration."""
        reply = QMessageBox.warning(
            self,
            "Reset Configuration",
            "Are you sure you want to reset all configuration?\n\nThis will delete your student info, modules, and logo.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.config.reset_config()
            QMessageBox.information(
                self,
                "Configuration Reset",
                "Configuration has been reset. The application will now close.\n\nPlease restart to set up again."
            )
            self.close()
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Lab Sheet Generator",
            "<h3>Lab Sheet Generator</h3>"
            "<p>Version 1.0.0</p>"
            "<p>A desktop application for university students to generate "
            "lab sheet templates automatically.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Automated lab sheet generation</li>"
            "<li>Custom university logo support</li>"
            "<li>Multiple module management</li>"
            "<li>Professional document formatting</li>"
            "</ul>"
        )