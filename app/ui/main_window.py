from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QSpinBox, QMessageBox, QGroupBox,
    QFormLayout, QFileDialog, QApplication
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QAction, QPixmap
from app.core.template_manager import get_template_manager
from app.core.theme_manager import ThemeManager
from app.utils.paths import get_output_dir
import os


class GeneratorThread(QThread):
    """Thread for generating lab sheets without blocking UI."""
    
    finished = Signal(str)  # Emits the output file path
    error = Signal(str)  # Emits error message
    
    def __init__(self, template, student_name, student_id, module_name, module_code, 
                 sheet_label, logo_path, output_dir):
        super().__init__()
        self.template = template
        self.student_name = student_name
        self.student_id = student_id
        self.module_name = module_name
        self.module_code = module_code
        self.sheet_label = sheet_label
        self.logo_path = logo_path
        self.output_dir = output_dir
    
    def run(self):
        """Generate the lab sheet."""
        try:
            # Generate in the output directory
            original_dir = os.getcwd()
            os.chdir(self.output_dir)
            
            output_file = self.template.generate(
                student_name=self.student_name,
                student_id=self.student_id,
                module_name=self.module_name,
                module_code=self.module_code,
                sheet_label=self.sheet_label,
                logo_path=str(self.logo_path) if self.logo_path else None
            )
            
            os.chdir(original_dir)
            
            # Return full path
            full_path = os.path.join(self.output_dir, output_file)
            self.finished.emit(full_path)
            
        except Exception as e:
            os.chdir(original_dir)
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window for generating lab sheets."""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.config_data = config.load_config()
        self.global_output_dir = self.config_data.get('global_output_path', str(get_output_dir()))
        self.generator_thread = None
        self.theme_manager = ThemeManager()
        
        # Set initial theme
        if self.config_data:
            self.theme_manager.set_theme(self.config_data.get('theme', 'light'))
        
        self.setWindowTitle("Lab Sheet Generator V2.0")
        self.setMinimumSize(700, 650)
        
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
        
        change_output_action = QAction("Change Default Output Folder", self)
        change_output_action.triggered.connect(self.change_global_output_folder)
        file_menu.addAction(change_output_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu (NEW in V2.0)
        view_menu = menubar.addMenu("View")
        
        current_theme = self.config_data.get('theme', 'light')
        theme_text = "Toggle Dark Mode" if current_theme == 'light' else "Toggle Light Mode"
        self.theme_action = QAction(theme_text, self)
        self.theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(self.theme_action)
        
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
    
    def toggle_theme(self):
        """Toggle between light and dark theme."""
        new_theme = self.theme_manager.toggle_theme()
        
        # Apply new theme to application
        QApplication.instance().setStyleSheet(self.theme_manager.get_stylesheet())
        
        # Save preference
        self.config.update_theme(new_theme)
        self.config_data['theme'] = new_theme
        
        # Update menu text
        if new_theme == 'dark':
            self.theme_action.setText("Toggle Light Mode")
        else:
            self.theme_action.setText("Toggle Dark Mode")
    
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
        self.logo_preview.setStyleSheet("border: 1px solid #ccc;")
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
        self.module_combo.currentIndexChanged.connect(self.on_module_changed)
        generator_layout.addRow("Select Module:", self.module_combo)
        
        # Sheet type display
        self.sheet_type_label = QLabel("Practical")
        self.sheet_type_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        generator_layout.addRow("Sheet Type:", self.sheet_type_label)
        
        # Template display and change button (NEW in V2.0)
        template_layout = QHBoxLayout()
        
        self.template_label = QLabel("Template: Classic")
        self.template_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        template_layout.addWidget(self.template_label)
        
        self.change_template_btn = QPushButton("Change Template")
        self.change_template_btn.setProperty("styleClass", "secondary")
        self.change_template_btn.clicked.connect(self.change_template)
        self.change_template_btn.setEnabled(False)
        template_layout.addWidget(self.change_template_btn)
        
        template_layout.addStretch()
        template_widget = QWidget()
        template_widget.setLayout(template_layout)
        generator_layout.addRow("Document:", template_widget)
        
        # Sheet number
        self.sheet_spin = QSpinBox()
        self.sheet_spin.setMinimum(1)
        self.sheet_spin.setMaximum(99)
        self.sheet_spin.setValue(1)
        self.sheet_spin.valueChanged.connect(self.update_filename_preview)
        generator_layout.addRow("Sheet Number:", self.sheet_spin)
        
        # Output path with browse button
        output_layout = QHBoxLayout()
        self.output_path_label = QLabel()
        self.output_path_label.setStyleSheet("font-size: 11px;")
        self.output_path_label.setWordWrap(True)
        output_layout.addWidget(self.output_path_label, 1)
        
        browse_output_btn = QPushButton("Browse...")
        browse_output_btn.setProperty("styleClass", "secondary")
        browse_output_btn.setMaximumWidth(80)
        browse_output_btn.clicked.connect(self.browse_module_output_path)
        output_layout.addWidget(browse_output_btn)
        
        output_widget = QWidget()
        output_widget.setLayout(output_layout)
        generator_layout.addRow("Output Path:", output_widget)
        
        # Filename preview
        self.filename_preview = QLabel()
        self.filename_preview.setStyleSheet("""
            padding: 8px;
            border: 1px solid;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            font-size: 10px;
        """)
        self.filename_preview.setWordWrap(True)
        generator_layout.addRow("Preview:", self.filename_preview)
        
        generator_group.setLayout(generator_layout)
        main_layout.addWidget(generator_group)
        
        # Generate button
        main_layout.addStretch()
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.generate_btn = QPushButton("Generate Lab Sheet")
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
        
        # Populate modules
        self.populate_modules()
    
    def update_student_info_display(self):
        """Update the student information display."""
        if self.config_data:
            name = self.config_data.get('student_name', 'N/A')
            student_id = self.config_data.get('student_id', 'N/A')
            self.student_info_label.setText(f"<b>Name:</b> {name}<br><b>ID:</b> {student_id}")
        else:
            self.student_info_label.setText("<i>No information available</i>")
    
    def populate_modules(self):
        """Populate the module combo box."""
        self.module_combo.clear()
        
        if not self.config_data or not self.config_data.get('modules'):
            self.module_combo.addItem("No modules configured", None)
            self.generate_btn.setEnabled(False)
            return
        
        for module in self.config_data['modules']:
            display_text = f"{module['name']} ({module['code']})"
            self.module_combo.addItem(display_text, module)
        
        self.generate_btn.setEnabled(True)
        
        # Trigger update for first module
        if self.module_combo.count() > 0:
            self.on_module_changed()
    
    def on_module_changed(self):
        """Handle module selection change."""
        module = self.module_combo.currentData()
        if not module:
            return
        
        # Update sheet type
        sheet_type = module.get('sheet_type', 'Practical')
        if sheet_type == 'Custom':
            sheet_type = module.get('custom_sheet_type', 'Sheet')
        self.sheet_type_label.setText(sheet_type)
        
        # Update template display (NEW in V2.0)
        template_id = module.get('template', 'classic')
        try:
            manager = get_template_manager()
            template = manager.get_template(template_id)
            self.template_label.setText(f"Template: {template.template_name}")
        except KeyError:
            self.template_label.setText(f"Template: {template_id.title()}")
        
        self.change_template_btn.setEnabled(True)
        
        # Update output path
        self.update_output_path_display()
        
        # Update filename preview
        self.update_filename_preview()
    
    def change_template(self):
        """Change template for current module."""
        from app.ui.template_selector import show_template_selector
        
        module = self.module_combo.currentData()
        if not module:
            return
        
        current_template = module.get('template', 'classic')
        selected = show_template_selector(current_template, self)
        
        if selected and selected != current_template:
            # Update module
            module['template'] = selected
            
            # Update display
            try:
                manager = get_template_manager()
                template = manager.get_template(selected)
                self.template_label.setText(f"Template: {template.template_name}")
            except KeyError:
                self.template_label.setText(f"Template: {selected.title()}")
            
            # Save config
            self.config.save_config(
                self.config_data['student_name'],
                self.config_data['student_id'],
                self.config_data['modules'],
                self.config_data['global_output_path'],
                self.config_data.get('theme', 'light'),
                self.config_data.get('default_template', 'classic')
            )
            
            # Reload config
            self.config_data = self.config.load_config()
    
    def update_output_path_display(self):
        """Update the output path display."""
        module = self.module_combo.currentData()
        if module:
            output_dir = module.get('output_path') or self.global_output_dir
            self.output_path_label.setText(output_dir)
    
    def browse_module_output_path(self):
        """Browse for module-specific output path."""
        module = self.module_combo.currentData()
        if not module:
            return
        
        current_path = module.get('output_path') or self.global_output_dir
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder for This Module",
            current_path
        )
        
        if folder:
            module['output_path'] = folder
            self.output_path_label.setText(folder)
            
            # Save config
            self.config.save_config(
                self.config_data['student_name'],
                self.config_data['student_id'],
                self.config_data['modules'],
                self.config_data['global_output_path'],
                self.config_data.get('theme', 'light'),
                self.config_data.get('default_template', 'classic')
            )
    
    def update_filename_preview(self):
        """Update the filename preview."""
        module = self.module_combo.currentData()
        if not module or not self.config_data:
            return
        
        # Build sheet label
        sheet_type = module.get('sheet_type', 'Practical')
        if sheet_type == 'Custom':
            sheet_type = module.get('custom_sheet_type', 'Sheet')
        
        sheet_num = self.sheet_spin.value()
        use_padding = module.get('use_zero_padding', True)
        
        if use_padding:
            sheet_label = f"{sheet_type} {sheet_num:02d}"
        else:
            sheet_label = f"{sheet_type} {sheet_num}"
        
        student_id = self.config_data['student_id']
        filename = f"{sheet_label.replace(' ', '_')}_{student_id}.docx"
        
        self.filename_preview.setText(f"📄 {filename}")
    
    def generate_lab_sheet(self):
        """Generate lab sheet using selected template."""
        module = self.module_combo.currentData()
        if not module:
            QMessageBox.warning(self, "No Module", "Please select a module.")
            return
        
        # Get template (NEW in V2.0)
        manager = get_template_manager()
        template_id = module.get('template', 'classic')
        
        try:
            template = manager.get_template(template_id)
        except KeyError:
            QMessageBox.critical(
                self, "Error",
                f"Template '{template_id}' not found. Using Classic template."
            )
            template = manager.get_template('classic')
            module['template'] = 'classic'
        
        # Build sheet label
        sheet_type = module.get('sheet_type', 'Practical')
        if sheet_type == 'Custom':
            sheet_type = module.get('custom_sheet_type', 'Sheet')
        
        sheet_num = self.sheet_spin.value()
        use_padding = module.get('use_zero_padding', True)
        
        if use_padding:
            sheet_label = f"{sheet_type} {sheet_num:02d}"
        else:
            sheet_label = f"{sheet_type} {sheet_num}"
        
        # Get output directory
        output_dir = module.get('output_path') or self.global_output_dir
        
        # Check logo
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
            logo_path = None
        
        # Disable button and show status
        self.generate_btn.setEnabled(False)
        self.status_label.setText("Generating lab sheet...")
        self.status_label.setStyleSheet("font-size: 12px; padding: 10px;")
        
        # Create and start generator thread
        self.generator_thread = GeneratorThread(
            template=template,
            student_name=self.config_data['student_name'],
            student_id=self.config_data['student_id'],
            module_name=module['name'],
            module_code=module['code'],
            sheet_label=sheet_label,
            logo_path=logo_path,
            output_dir=output_dir
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
            folder_path = os.path.dirname(file_path)
            self.open_folder(folder_path)
    
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
        """Open the current module's output folder or default folder."""
        module = self.module_combo.currentData()
        if module:
            output_dir = module.get('output_path') or self.global_output_dir
        else:
            output_dir = self.global_output_dir
        
        self.open_folder(output_dir)
    
    def open_folder(self, folder_path):
        """Open a folder in the file explorer."""
        if os.name == 'nt':  # Windows
            os.startfile(folder_path)
        elif os.name == 'posix':  # macOS/Linux
            import subprocess
            if os.uname().sysname == 'Darwin':
                subprocess.run(['open', folder_path])
            else:
                subprocess.run(['xdg-open', folder_path])
    
    def change_global_output_folder(self):
        """Change the default global output folder."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Default Output Folder",
            self.global_output_dir
        )
        
        if folder:
            self.global_output_dir = folder
            
            # Update config
            self.config_data['global_output_path'] = folder
            self.config.save_config(
                self.config_data['student_name'],
                self.config_data['student_id'],
                self.config_data['modules'],
                folder,
                self.config_data.get('theme', 'light'),
                self.config_data.get('default_template', 'classic')
            )
            
            # Update display if current module uses default
            self.update_output_path_display()
            
            QMessageBox.information(
                self,
                "Output Folder Changed",
                f"Default output folder changed to:\n{folder}\n\nModules without a specific output path will use this location."
            )
    
    def edit_configuration(self):
        """Open setup wizard to edit configuration."""
        from app.ui.setup_window import SetupWindow
        
        setup_window = SetupWindow(self.config)
        
        # Pre-fill with existing data
        setup_window.name_input.setText(self.config_data.get('student_name', ''))
        setup_window.id_input.setText(self.config_data.get('student_id', ''))
        
        # Pre-fill modules
        setup_window.modules = self.config_data.get('modules', []).copy()
        setup_window.update_module_list_display()
        
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
            self.global_output_dir = self.config_data.get('global_output_path', str(get_output_dir()))
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
            "<h3>Lab Sheet Generator V2.0.0</h3>"
            "<p>A desktop application for university students to generate "
            "lab sheet templates automatically.</p>"
            "<p><b>New in V2.0:</b></p>"
            "<ul>"
            "<li>🎨 Modern Apple-like UI design</li>"
            "<li>🌓 Light and Dark themes</li>"
            "<li>📄 Multiple document templates</li>"
            "<li>✨ Enhanced user experience</li>"
            "<li>🔧 Improved configuration system</li>"
            "</ul>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Automated lab sheet generation</li>"
            "<li>Custom university logo support</li>"
            "<li>Multiple module management</li>"
            "<li>Per-module output paths and templates</li>"
            "<li>Configurable sheet types</li>"
            "<li>Professional document formatting</li>"
            "</ul>"
        )