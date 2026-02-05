from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFileDialog, QMessageBox, QListWidget, 
    QDialog, QDialogButtonBox, QFormLayout, QGroupBox, QComboBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from app.utils.validators import (
    validate_student_name, validate_student_id, 
    validate_module_name, validate_module_code
)


class ModuleDialog(QDialog):
    """Dialog for adding/editing a module with enhanced configuration."""
    
    def __init__(self, parent=None, module_data=None):
        super().__init__(parent)
        self.setWindowTitle("Add Module" if not module_data else "Edit Module")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        # Create form layout
        layout = QFormLayout()
        
        # Module name input
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Programming Paradigms")
        layout.addRow("Module Name:", self.name_input)
        
        # Module code input
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("e.g., SE2052")
        self.code_input.setMaxLength(10)
        layout.addRow("Module Code:", self.code_input)
        
        # Sheet type selection
        self.sheet_type_combo = QComboBox()
        self.sheet_type_combo.addItems([
            "Practical",
            "Lab",
            "Worksheet",
            "Tutorial",
            "Assignment",
            "Exercise",
            "Custom"
        ])
        self.sheet_type_combo.currentTextChanged.connect(self.on_sheet_type_changed)
        layout.addRow("Sheet Type:", self.sheet_type_combo)
        
        # Custom sheet type input (hidden by default)
        self.custom_type_input = QLineEdit()
        self.custom_type_input.setPlaceholderText("e.g., Problem Set, Case Study")
        self.custom_type_input.setVisible(False)
        layout.addRow("Custom Type:", self.custom_type_input)
        
        # Output path selection
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Leave empty to use default location")
        path_layout.addWidget(self.path_input)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_output_path)
        path_layout.addWidget(browse_btn)
        
        path_widget = QWidget()
        path_widget.setLayout(path_layout)
        layout.addRow("Output Path:", path_widget)
        
        # Info label
        info_label = QLabel("💡 Tip: Choose a folder specific to this module for better organization")
        info_label.setStyleSheet("color: gray; font-size: 10px; font-style: italic;")
        info_label.setWordWrap(True)
        layout.addRow("", info_label)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
        
        self.setLayout(layout)
        
        # Pre-fill if editing
        if module_data:
            self.load_module_data(module_data)
    
    def load_module_data(self, module_data):
        """Load existing module data into form fields."""
        self.name_input.setText(module_data.get('name', ''))
        self.code_input.setText(module_data.get('code', ''))
        
        sheet_type = module_data.get('sheet_type', 'Practical')
        index = self.sheet_type_combo.findText(sheet_type)
        if index >= 0:
            self.sheet_type_combo.setCurrentIndex(index)
        
        custom_type = module_data.get('custom_sheet_type', '')
        if custom_type:
            self.custom_type_input.setText(custom_type)
        
        output_path = module_data.get('output_path', '')
        if output_path:
            self.path_input.setText(output_path)
    
    def on_sheet_type_changed(self, text):
        """Show/hide custom type input based on selection."""
        is_custom = text == "Custom"
        self.custom_type_input.setVisible(is_custom)
        
        # Find the custom type row and show/hide it
        for i in range(self.layout().rowCount()):
            label = self.layout().itemAt(i, QFormLayout.LabelRole)
            if label and label.widget():
                if label.widget().text() == "Custom Type:":
                    label.widget().setVisible(is_custom)
        
        # Adjust dialog size
        self.adjustSize()
    
    def browse_output_path(self):
        """Open folder selection dialog."""
        current_path = self.path_input.text() or ""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder for This Module",
            current_path
        )
        if folder:
            self.path_input.setText(folder)
    
    def validate_and_accept(self):
        """Validate inputs before accepting."""
        name = self.name_input.text().strip()
        code = self.code_input.text().strip().upper()
        sheet_type = self.sheet_type_combo.currentText()
        custom_type = self.custom_type_input.text().strip()
        
        # Validate module name
        is_valid, error = validate_module_name(name)
        if not is_valid:
            QMessageBox.warning(self, "Invalid Input", error)
            return
        
        # Validate module code
        is_valid, error = validate_module_code(code)
        if not is_valid:
            QMessageBox.warning(self, "Invalid Input", error)
            return
        
        # Validate custom type if selected
        if sheet_type == "Custom" and not custom_type:
            QMessageBox.warning(
                self, 
                "Invalid Input", 
                "Please enter a custom sheet type or select a predefined type"
            )
            return
        
        self.accept()
    
    def get_module(self):
        """Get the module data with enhanced fields."""
        sheet_type = self.sheet_type_combo.currentText()
        custom_type = self.custom_type_input.text().strip() if sheet_type == "Custom" else None
        output_path = self.path_input.text().strip() or None
        
        return {
            'name': self.name_input.text().strip(),
            'code': self.code_input.text().strip().upper(),
            'sheet_type': sheet_type,
            'custom_sheet_type': custom_type,
            'output_path': output_path,
            'use_zero_padding': True  # Default to zero padding
        }


class SetupWindow(QWidget):
    """First-time setup wizard window."""
    
    setup_complete = Signal(dict)  # Emits config data when setup is complete
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.logo_path = None
        self.modules = []
        
        self.setWindowTitle("Lab Sheet Generator - Setup")
        self.setMinimumSize(600, 500)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout()
        
        # Title
        title = QLabel("Welcome to Lab Sheet Generator!")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        subtitle = QLabel("Let's set up your information")
        subtitle.setStyleSheet("font-size: 12px; color: gray; margin-bottom: 20px;")
        subtitle.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle)
        
        # Student Information Group
        student_group = QGroupBox("Student Information")
        student_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., NONIS P.K.D.T.")
        student_layout.addRow("Full Name:", self.name_input)
        
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("e.g., IT23614130")
        student_layout.addRow("Student ID:", self.id_input)
        
        student_group.setLayout(student_layout)
        main_layout.addWidget(student_group)
        
        # Logo Section
        logo_group = QGroupBox("University Logo")
        logo_layout = QVBoxLayout()
        
        logo_btn_layout = QHBoxLayout()
        self.logo_btn = QPushButton("Upload Logo")
        self.logo_btn.clicked.connect(self.select_logo)
        logo_btn_layout.addWidget(self.logo_btn)
        
        self.logo_label = QLabel("No logo selected")
        self.logo_label.setStyleSheet("color: gray; font-style: italic;")
        logo_btn_layout.addWidget(self.logo_label)
        logo_btn_layout.addStretch()
        
        logo_layout.addLayout(logo_btn_layout)
        
        # Logo preview
        self.logo_preview = QLabel()
        self.logo_preview.setFixedSize(110, 105)
        self.logo_preview.setStyleSheet("border: 1px solid #ccc; background: #f5f5f5;")
        self.logo_preview.setAlignment(Qt.AlignCenter)
        self.logo_preview.setText("Preview")
        logo_layout.addWidget(self.logo_preview)
        
        logo_group.setLayout(logo_layout)
        main_layout.addWidget(logo_group)
        
        # Modules Section
        modules_group = QGroupBox("Modules")
        modules_layout = QVBoxLayout()
        
        modules_info = QLabel("Add your modules for this semester:")
        modules_info.setStyleSheet("color: gray; font-size: 11px;")
        modules_layout.addWidget(modules_info)
        
        # Module list
        self.module_list = QListWidget()
        self.module_list.setMaximumHeight(120)
        modules_layout.addWidget(self.module_list)
        
        # Module buttons
        module_btn_layout = QHBoxLayout()
        
        add_module_btn = QPushButton("Add Module")
        add_module_btn.clicked.connect(self.add_module)
        module_btn_layout.addWidget(add_module_btn)
        
        self.edit_module_btn = QPushButton("Edit Module")
        self.edit_module_btn.clicked.connect(self.edit_module)
        self.edit_module_btn.setEnabled(False)
        module_btn_layout.addWidget(self.edit_module_btn)
        
        self.remove_module_btn = QPushButton("Remove Module")
        self.remove_module_btn.clicked.connect(self.remove_module)
        self.remove_module_btn.setEnabled(False)
        module_btn_layout.addWidget(self.remove_module_btn)
        
        module_btn_layout.addStretch()
        modules_layout.addLayout(module_btn_layout)
        
        modules_group.setLayout(modules_layout)
        main_layout.addWidget(modules_group)
        
        # Bottom buttons
        main_layout.addStretch()
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.finish_btn = QPushButton("Finish Setup")
        self.finish_btn.setStyleSheet("""
            QPushButton {
                background-color: #156082;
                color: white;
                padding: 8px 20px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1a7599;
            }
        """)
        self.finish_btn.clicked.connect(self.finish_setup)
        button_layout.addWidget(self.finish_btn)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # Connect list selection change
        self.module_list.itemSelectionChanged.connect(self.on_module_selection_changed)
    
    def select_logo(self):
        """Open file dialog to select logo."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select University Logo",
            "",
            "Image Files (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            self.logo_path = file_path
            self.logo_label.setText(file_path.split('/')[-1])
            self.logo_label.setStyleSheet("color: green;")
            
            # Show preview
            pixmap = QPixmap(file_path)
            scaled_pixmap = pixmap.scaled(
                110, 105, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.logo_preview.setPixmap(scaled_pixmap)
    
    def add_module(self):
        """Open dialog to add a new module."""
        dialog = ModuleDialog(self)
        if dialog.exec():
            module = dialog.get_module()
            self.modules.append(module)
            self.update_module_list_display()
    
    def edit_module(self):
        """Edit the selected module."""
        current_row = self.module_list.currentRow()
        if current_row >= 0:
            module = self.modules[current_row]
            dialog = ModuleDialog(self, module)
            if dialog.exec():
                updated_module = dialog.get_module()
                self.modules[current_row] = updated_module
                self.update_module_list_display()
    
    def remove_module(self):
        """Remove selected module."""
        current_row = self.module_list.currentRow()
        if current_row >= 0:
            module = self.modules[current_row]
            reply = QMessageBox.question(
                self,
                "Remove Module",
                f"Are you sure you want to remove '{module['name']}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.module_list.takeItem(current_row)
                self.modules.pop(current_row)
    
    def update_module_list_display(self):
        """Update the module list display with enhanced info."""
        self.module_list.clear()
        for module in self.modules:
            sheet_type = module.get('sheet_type', 'Practical')
            if sheet_type == 'Custom':
                sheet_type = module.get('custom_sheet_type', 'Custom')
            
            path_indicator = " 📁" if module.get('output_path') else ""
            display_text = f"{module['name']} ({module['code']}) - {sheet_type}{path_indicator}"
            self.module_list.addItem(display_text)
    
    def on_module_selection_changed(self):
        """Enable/disable edit and remove buttons based on selection."""
        has_selection = self.module_list.currentRow() >= 0
        self.edit_module_btn.setEnabled(has_selection)
        self.remove_module_btn.setEnabled(has_selection)
    
    def finish_setup(self):
        """Validate and save configuration."""
        # Validate student name
        name = self.name_input.text().strip()
        is_valid, error = validate_student_name(name)
        if not is_valid:
            QMessageBox.warning(self, "Invalid Input", f"Student Name: {error}")
            return
        
        # Validate student ID
        student_id = self.id_input.text().strip()
        is_valid, error = validate_student_id(student_id)
        if not is_valid:
            QMessageBox.warning(self, "Invalid Input", f"Student ID: {error}")
            return
        
        # Check logo
        if not self.logo_path:
            reply = QMessageBox.question(
                self,
                "No Logo",
                "You haven't selected a logo. Continue without logo?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Check modules
        if not self.modules:
            reply = QMessageBox.question(
                self,
                "No Modules",
                "You haven't added any modules. Continue anyway?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Save configuration with enhanced module data
        self.config.save_config(name, student_id, self.modules)
        
        # Save logo if provided
        if self.logo_path:
            self.config.save_logo(self.logo_path)
        
        # Show success message
        QMessageBox.information(
            self,
            "Setup Complete",
            "Your configuration has been saved successfully!"
        )
        
        # Emit signal with config data
        config_data = {
            'student_name': name,
            'student_id': student_id,
            'modules': self.modules,
            'logo_path': self.config.get_logo_path()
        }
        self.setup_complete.emit(config_data)
        
        # Close window
        self.close()