"""
Modern GUI for JARVIS Voice Assistant
Features: Dark/Light themes, Language selection, Voice visualization, Command history
"""

import sys
import os
import json
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.animation as animation

class VoiceVisualizationWidget(FigureCanvas):
    """Voice activity visualization widget"""
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(8, 2), facecolor='black')
        super().__init__(self.fig)
        self.setParent(parent)
        
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('black')
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(-1, 1)
        self.ax.axis('off')
        
        # Initialize data
        self.x_data = np.linspace(0, 100, 100)
        self.y_data = np.zeros(100)
        self.line, = self.ax.plot(self.x_data, self.y_data, '#00ff41', linewidth=2)
        
        self.is_listening = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_visualization)
    
    def start_visualization(self):
        """Start voice visualization"""
        self.is_listening = True
        self.timer.start(50)  # Update every 50ms
    
    def stop_visualization(self):
        """Stop voice visualization"""
        self.is_listening = False
        self.timer.stop()
        self.y_data = np.zeros(100)
        self.update_plot()
    
    def update_visualization(self):
        """Update voice visualization with random data (placeholder)"""
        if self.is_listening:
            # Simulate audio input (replace with real audio data)
            amplitude = np.random.random() * 0.8
            frequency = 2 + np.random.random() * 3
            phase = np.random.random() * 2 * np.pi
            
            self.y_data = amplitude * np.sin(frequency * self.x_data * 0.1 + phase)
        else:
            self.y_data = np.zeros(100)
        
        self.update_plot()
    
    def update_plot(self):
        """Update the plot"""
        self.line.set_ydata(self.y_data)
        self.draw()

class CommandHistoryWidget(QWidget):
    """Widget to display command history"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.command_history = []
        self.max_history = 50
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Command History")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00ff41; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # History list
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(30, 30, 30, 150);
                border: 1px solid #00ff41;
                border-radius: 10px;
                color: white;
                font-size: 12px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #333;
            }
            QListWidget::item:selected {
                background-color: #00ff41;
                color: black;
            }
        """)
        layout.addWidget(self.history_list)
        
        # Clear button
        clear_btn = QPushButton("Clear History")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
        """)
        clear_btn.clicked.connect(self.clear_history)
        layout.addWidget(clear_btn)
        
        self.setLayout(layout)
    
    def add_command(self, command, response):
        """Add command to history"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {command} → {response[:50]}..."
        
        self.command_history.append(entry)
        self.history_list.addItem(entry)
        
        # Limit history size
        if len(self.command_history) > self.max_history:
            self.command_history.pop(0)
            self.history_list.takeItem(0)
        
        # Auto scroll to bottom
        self.history_list.scrollToBottom()
    
    def clear_history(self):
        """Clear command history"""
        self.command_history.clear()
        self.history_list.clear()

class LanguageSelectionWidget(QWidget):
    """Language selection widget"""
    language_changed = pyqtSignal(str)
    
    def __init__(self, language_support):
        super().__init__()
        self.language_support = language_support
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Language Settings")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00ff41; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Language dropdown
        self.language_combo = QComboBox()
        self.language_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(30, 30, 30, 150);
                border: 1px solid #00ff41;
                border-radius: 5px;
                padding: 8px;
                color: white;
                font-size: 12px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                color: #00ff41;
            }
            QComboBox QAbstractItemView {
                background-color: #2a2a2a;
                border: 1px solid #00ff41;
                selection-background-color: #00ff41;
                selection-color: black;
                color: white;
            }
        """)
        
        # Populate languages
        languages = self.language_support.get_available_languages()
        for code, name in languages:
            self.language_combo.addItem(name, code)
        
        self.language_combo.currentTextChanged.connect(self.on_language_changed)
        layout.addWidget(self.language_combo)
        
        # Current language display
        self.current_lang_label = QLabel("Current: English")
        self.current_lang_label.setStyleSheet("color: #00ff41; font-size: 12px; margin-top: 10px;")
        layout.addWidget(self.current_lang_label)
        
        self.setLayout(layout)
    
    def on_language_changed(self, language_name):
        """Handle language change"""
        code = self.language_combo.currentData()
        self.language_changed.emit(code)
        self.current_lang_label.setText(f"Current: {language_name}")

class StatusWidget(QWidget):
    """Status display widget"""
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Status indicator
        self.status_label = QLabel("● OFFLINE")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ff4444;")
        layout.addWidget(self.status_label)
        
        # Activity text
        self.activity_label = QLabel("Ready to assist...")
        self.activity_label.setStyleSheet("font-size: 12px; color: #cccccc;")
        layout.addWidget(self.activity_label)
        
        self.setLayout(layout)
    
    def set_status(self, status, color="#ff4444"):
        """Set status text and color"""
        self.status_label.setText(f"● {status}")
        self.status_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {color};")
    
    def set_activity(self, activity):
        """Set activity text"""
        self.activity_label.setText(activity)

class ModernJarvisGUI(QMainWindow):
    """Modern JARVIS GUI main window"""
    
    def __init__(self, language_support=None):
        super().__init__()
        self.language_support = language_support
        self.is_dark_theme = True
        self.init_ui()
        self.setup_themes()
        self.apply_theme()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("JARVIS - Advanced Voice Assistant")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Center panel
        center_panel = self.create_center_panel()
        main_layout.addWidget(center_panel, 2)
        
        # Right panel
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 1)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Menu bar
        self.create_menu_bar()
    
    def create_left_panel(self):
        """Create left control panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Logo/Title
        title = QLabel("J.A.R.V.I.S")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #00ff41;
            margin: 20px;
            text-shadow: 2px 2px 4px rgba(0,255,65,0.3);
        """)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Just A Rather Very Intelligent System")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 12px; color: #cccccc; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        # Status widget
        self.status_widget = StatusWidget()
        layout.addWidget(self.status_widget)
        
        # Control buttons
        button_layout = QVBoxLayout()
        
        self.start_btn = QPushButton("🎙️ START LISTENING")
        self.start_btn.setStyleSheet(self.get_button_style("#00ff41"))
        self.start_btn.clicked.connect(self.start_listening)
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹️ STOP")
        self.stop_btn.setStyleSheet(self.get_button_style("#ff4444"))
        self.stop_btn.clicked.connect(self.stop_listening)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        self.settings_btn = QPushButton("⚙️ SETTINGS")
        self.settings_btn.setStyleSheet(self.get_button_style("#4444ff"))
        self.settings_btn.clicked.connect(self.open_settings)
        button_layout.addWidget(self.settings_btn)
        
        self.theme_btn = QPushButton("🌓 TOGGLE THEME")
        self.theme_btn.setStyleSheet(self.get_button_style("#ff8800"))
        self.theme_btn.clicked.connect(self.toggle_theme)
        button_layout.addWidget(self.theme_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        return panel
    
    def create_center_panel(self):
        """Create center display panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Voice visualization
        self.voice_viz = VoiceVisualizationWidget()
        layout.addWidget(self.voice_viz)
        
        # Main display area
        self.main_display = QTextEdit()
        self.main_display.setReadOnly(True)
        self.main_display.setStyleSheet("""
            QTextEdit {
                background-color: rgba(30, 30, 30, 200);
                border: 2px solid #00ff41;
                border-radius: 15px;
                color: #00ff41;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 14px;
                padding: 15px;
            }
        """)
        self.main_display.append("🤖 JARVIS System Initialized")
        self.main_display.append("Ready to receive voice commands...")
        layout.addWidget(self.main_display)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Type a command or speak to JARVIS...")
        self.text_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(30, 30, 30, 150);
                border: 1px solid #00ff41;
                border-radius: 20px;
                padding: 10px 15px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #00ff41;
                box-shadow: 0 0 10px rgba(0,255,65,0.3);
            }
        """)
        self.text_input.returnPressed.connect(self.process_text_input)
        input_layout.addWidget(self.text_input)
        
        send_btn = QPushButton("SEND")
        send_btn.setStyleSheet(self.get_button_style("#00ff41"))
        send_btn.clicked.connect(self.process_text_input)
        input_layout.addWidget(send_btn)
        
        layout.addLayout(input_layout)
        
        return panel
    
    def create_right_panel(self):
        """Create right information panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Time and date display
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #00ff41;
            background-color: rgba(30, 30, 30, 150);
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
        """)
        layout.addWidget(self.time_label)
        
        # Language selection
        if self.language_support:
            self.language_widget = LanguageSelectionWidget(self.language_support)
            self.language_widget.language_changed.connect(self.change_language)
            layout.addWidget(self.language_widget)
        
        # Command history
        self.history_widget = CommandHistoryWidget()
        layout.addWidget(self.history_widget)
        
        # Info panel
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        
        info_title = QLabel("System Information")
        info_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #00ff41;")
        info_layout.addWidget(info_title)
        
        self.info_text = QLabel("CPU: 0%\nRAM: 0%\nLanguage: English")
        self.info_text.setStyleSheet("""
            background-color: rgba(30, 30, 30, 150);
            border: 1px solid #333;
            border-radius: 8px;
            padding: 10px;
            color: #cccccc;
            font-size: 11px;
        """)
        info_layout.addWidget(self.info_text)
        
        layout.addWidget(info_widget)
        layout.addStretch()
        
        # Timer for updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(1000)
        
        return panel
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        settings_action = QAction('Settings', self)
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)
        
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        theme_action = QAction('Toggle Theme', self)
        theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(theme_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def get_button_style(self, color):
        """Get button style with specified color"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 25px;
                font-weight: bold;
                font-size: 12px;
                margin: 5px 0;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
                transform: scale(1.05);
            }}
            QPushButton:pressed {{
                background-color: {color}aa;
            }}
            QPushButton:disabled {{
                background-color: #666666;
            }}
        """
    
    def setup_themes(self):
        """Setup theme configurations"""
        self.themes = {
            'dark': {
                'background': '#1a1a1a',
                'text': '#ffffff',
                'accent': '#00ff41',
                'panel': 'rgba(30, 30, 30, 200)'
            },
            'light': {
                'background': '#f0f0f0',
                'text': '#000000',
                'accent': '#007700',
                'panel': 'rgba(255, 255, 255, 200)'
            }
        }
    
    def apply_theme(self):
        """Apply the current theme"""
        theme = self.themes['dark' if self.is_dark_theme else 'light']
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme['background']};
                color: {theme['text']};
            }}
            QWidget {{
                background-color: transparent;
                color: {theme['text']};
            }}
        """)
    
    def toggle_theme(self):
        """Toggle between dark and light themes"""
        self.is_dark_theme = not self.is_dark_theme
        self.apply_theme()
        self.append_to_display("🎨 Theme toggled")
    
    def update_display(self):
        """Update time and system information"""
        current_time = datetime.now()
        time_str = current_time.strftime("%H:%M:%S\n%Y-%m-%d")
        self.time_label.setText(time_str)
        
        # Update system info (placeholder)
        try:
            import psutil
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            lang_info = self.language_support.get_current_language_info() if self.language_support else {'name': 'English'}
            
            info_text = f"CPU: {cpu_percent}%\nRAM: {memory.percent}%\nLanguage: {lang_info['name']}"
            self.info_text.setText(info_text)
        except:
            pass
    
    def start_listening(self):
        """Start voice listening"""
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_widget.set_status("LISTENING", "#00ff41")
        self.status_widget.set_activity("Waiting for voice input...")
        self.voice_viz.start_visualization()
        self.append_to_display("🎤 Voice recognition started")
    
    def stop_listening(self):
        """Stop voice listening"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_widget.set_status("OFFLINE", "#ff4444")
        self.status_widget.set_activity("Ready to assist...")
        self.voice_viz.stop_visualization()
        self.append_to_display("⏹️ Voice recognition stopped")
    
    def process_text_input(self):
        """Process text input"""
        text = self.text_input.text().strip()
        if text:
            self.append_to_display(f"👤 You: {text}")
            self.text_input.clear()
            # Here you would process the command with JARVIS
            response = "Command received and processing..."
            self.append_to_display(f"🤖 JARVIS: {response}")
            self.history_widget.add_command(text, response)
    
    def change_language(self, language_code):
        """Change the system language"""
        if self.language_support:
            if self.language_support.set_language(language_code):
                lang_name = self.language_support.supported_languages[language_code]
                self.append_to_display(f"🌐 Language changed to {lang_name}")
                self.history_widget.add_command(f"Change language to {lang_name}", "Language changed successfully")
    
    def append_to_display(self, text):
        """Append text to main display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.main_display.append(f"[{timestamp}] {text}")
        
        # Auto scroll to bottom
        cursor = self.main_display.textCursor()
        cursor.movePosition(cursor.End)
        self.main_display.setTextCursor(cursor)
    
    def open_settings(self):
        """Open settings dialog"""
        QMessageBox.information(self, "Settings", "Settings panel coming soon!")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        JARVIS - Just A Rather Very Intelligent System
        
        Advanced Voice Assistant with Multi-language Support
        
        Features:
        • Voice Recognition in Multiple Languages
        • Modern Dark/Light Theme Interface
        • Real-time Voice Visualization
        • Command History
        • System Monitoring
        
        Version: 3.0
        """
        QMessageBox.about(self, "About JARVIS", about_text)
    
    def closeEvent(self, event):
        """Handle close event"""
        reply = QMessageBox.question(self, 'Exit JARVIS', 
                                   'Are you sure you want to exit JARVIS?',
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

def main():
    """Main function to run the GUI"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("JARVIS")
    app.setApplicationVersion("3.0")
    app.setOrganizationName("JARVIS Systems")
    
    # Create and show the GUI
    gui = ModernJarvisGUI()
    gui.show()
    
    return app.exec_()

if __name__ == '__main__':
    main()