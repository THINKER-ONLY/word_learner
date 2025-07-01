from PyQt6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QFormLayout, QLabel, QSpinBox, QComboBox, QCheckBox

class SettingsDialog(QDialog):
    def __init__(self, settings_manager, parent=None):
        """
        初始化设置对话框。
        :param settings_manager: An instance of the SettingsManager.
        :param parent: 父窗口。
        """
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.settings_manager = settings_manager

        # --- Layouts and Widgets ---
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Display Interval (seconds)
        self.interval_input = QSpinBox(self)
        self.interval_input.setMinimum(1)
        self.interval_input.setMaximum(60)
        self.interval_input.setSuffix(" seconds")

        # Display Mode (random/sequential)
        self.mode_input = QComboBox(self)
        self.mode_input.addItems(["random", "sequential"])

        # Show Chinese Translation
        self.show_chinese_input = QCheckBox("Show translation by default")
        
        form_layout.addRow(QLabel("Word Display Interval:"), self.interval_input)
        form_layout.addRow(QLabel("Word Display Mode:"), self.mode_input)
        form_layout.addRow(self.show_chinese_input)
        
        layout.addLayout(form_layout)

        # --- Dialog Buttons (OK/Cancel) ---
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept) # accept calls our overridden method
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self._load_current_settings()

    def _load_current_settings(self):
        """Loads settings from the manager and populates the UI fields."""
        interval = self.settings_manager.get_settings("display_interval")
        self.interval_input.setValue(interval)

        mode = self.settings_manager.get_settings("display_mode")
        self.mode_input.setCurrentText(mode)

        show_chinese = self.settings_manager.get_settings("show_chinese")
        self.show_chinese_input.setChecked(show_chinese)
        
    def _save_settings(self):
        """Saves the current values from UI fields back to the settings manager."""
        self.settings_manager.set_settings("display_interval", self.interval_input.value())
        self.settings_manager.set_settings("display_mode", self.mode_input.currentText())
        self.settings_manager.set_settings("show_chinese", self.show_chinese_input.isChecked())
    
    def accept(self):
        """Overrides the default accept to save settings before closing."""
        self._save_settings()
        super().accept() 