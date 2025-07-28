"""
Enhanced JARVIS Main Application
Features: Multi-language support, Modern GUI, Better performance, Enhanced commands
"""

import sys
import os
import re
import random
import datetime
import requests
import time
import pyautogui
import pywhatkit
import wolframalpha
from PIL import Image
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QTimer, QTime, QDate, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import *

# Import JARVIS components
from Jarvis import JarvisAssistant
from Jarvis.features.modern_gui import ModernJarvisGUI
from Jarvis.config import config

# Initialize JARVIS
obj = JarvisAssistant()

# ================================ ENHANCED MEMORY ===========================================================================================================

GREETINGS = [
    "hello jarvis", "jarvis", "wake up jarvis", "you there jarvis", "time to work jarvis", "hey jarvis",
    "ok jarvis", "are you there", "hi jarvis", "good morning jarvis", "good afternoon jarvis", "good evening jarvis",
    # Multi-language greetings
    "नमस्ते jarvis", "जार्विस", "السلام علیکم jarvis", "سلام جارویس"
]

GREETINGS_RES = [
    "always there for you sir", "i am ready sir", "your wish my command", "how can i help you sir?", 
    "i am online and ready sir", "at your service", "ready to assist you", "how may I help you today?",
    "good to see you back", "what can I do for you?"
]

EMAIL_DIC = {
    'myself': 'your_email@gmail.com',
    'my official email': 'your_email@gmail.com',
    'my second email': 'your_email@gmail.com',
    'boss': 'boss@company.com',
    'team': 'team@company.com'
}

CALENDAR_STRS = ["what do i have", "do i have plans", "am i busy", "my schedule", "what's on my calendar"]

# ================================ ENHANCED FUNCTIONS ===========================================================================================================

def speak(text):
    """Enhanced speak function with language support"""
    obj.tts(text)

def startup():
    """Enhanced startup with better feedback"""
    startup_messages = [
        "🚀 Initializing JARVIS Enhanced Assistant",
        "🔧 Starting all systems applications",
        "📦 Installing and checking all drivers",
        "🧠 Calibrating and examining all the core processors",
        "🌐 Checking the internet connection",
        "⏳ Please wait a moment...",
        "✅ All drivers are up and running",
        "🎯 All systems have been activated",
        "🔴 Now I am online and ready"
    ]
    
    for message in startup_messages:
        print(message)
        speak(message.split(' ', 1)[1])  # Remove emoji for speech
        time.sleep(0.5)
    
    # Get performance stats
    stats = obj.get_performance_stats()
    current_lang = stats['current_language']['name']
    
    speak(f"Language set to {current_lang}")
    
    # Time-based greeting
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour <= 12:
        greeting = obj.language_support.get_template('greeting')
        speak(greeting)
    elif hour > 12 and hour < 18:
        speak("Good afternoon")
    else:
        speak("Good evening")
    
    # Tell current time
    c_time = obj.tell_time()
    time_message = obj.language_support.get_template('time_response', time=c_time)
    speak(time_message)
    
    # Final ready message
    ready_message = "I am JARVIS Enhanced Assistant. Online and ready sir. Please tell me how may I help you"
    speak(ready_message)

def get_computational_intelligence_response(question):
    """Enhanced computational intelligence with error handling"""
    try:
        app_id = config.wolframalpha_id
        if not app_id or app_id == "<your_wolframalpha_id>":
            return "Wolfram Alpha API key not configured. Please add your API key to config.py"
        
        client = wolframalpha.Client(app_id)
        answer = client.query(question)
        answer_text = next(answer.results).text
        print(f"🧠 Computational result: {answer_text}")
        return answer_text
    except Exception as e:
        error_msg = obj.error_handler.handle_error('api_error', e, 'computational_intelligence')
        return error_msg

def wish():
    """Enhanced wish function"""
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour <= 12:
        speak("Good Morning")
    elif hour > 12 and hour < 18:
        speak("Good afternoon")
    else:
        speak("Good evening")
    
    c_time = obj.tell_time()
    time_message = obj.language_support.get_template('time_response', time=c_time)
    speak(time_message)
    
    ready_message = "I am JARVIS Enhanced Assistant. Online and ready sir. Please tell me how may I help you"
    speak(ready_message)

# ================================ ENHANCED MAIN THREAD ===========================================================================================================

class EnhancedMainThread(QThread):
    """Enhanced main thread with better error handling and performance"""
    
    status_update = pyqtSignal(str)
    command_processed = pyqtSignal(str, str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super(EnhancedMainThread, self).__init__()
        self.is_running = True
        self.command_count = 0
    
    def run(self):
        """Main execution thread"""
        try:
            self.TaskExecution()
        except Exception as e:
            error_msg = obj.error_handler.handle_error('system_error', e, 'main_thread')
            self.error_occurred.emit(error_msg)
    
    def stop(self):
        """Stop the thread gracefully"""
        self.is_running = False
        obj.cleanup()
    
    def TaskExecution(self):
        """Enhanced task execution with intelligent command processing"""
        # Startup sequence
        startup()
        wish()
        
        self.status_update.emit("🎤 Ready for voice commands")
        
        while self.is_running:
            try:
                # Get voice input
                self.status_update.emit("👂 Listening...")
                command = obj.mic_input()
                
                if not command or command == False:
                    continue
                
                self.command_count += 1
                self.status_update.emit(f"🎯 Processing command #{self.command_count}")
                
                # Process command intelligently
                response = self.process_command_intelligently(command)
                
                # Emit signals for GUI updates
                self.command_processed.emit(command, response)
                
                # Speak the response
                if response:
                    speak(response)
                
                # Add small delay to prevent overwhelming
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                self.stop()
                break
            except Exception as e:
                error_msg = obj.error_handler.handle_error('system_error', e, 'task_execution')
                self.error_occurred.emit(error_msg)
                speak(error_msg)
    
    def process_command_intelligently(self, command):
        """Process commands using enhanced intelligence"""
        try:
            # Use the enhanced command processor
            response = obj.process_command_intelligently(command)
            
            if response:
                return response
            
            # Handle specific legacy commands that might not be covered
            command_lower = command.lower()
            
            # Launch application
            if 'launch' in command_lower:
                app_dict = {
                    'chrome': 'C:/Program Files/Google/Chrome/Application/chrome.exe',
                    'firefox': 'C:/Program Files/Mozilla Firefox/firefox.exe',
                    'notepad': 'notepad.exe',
                    'calculator': 'calc.exe',
                    'paint': 'mspaint.exe'
                }
                
                app_name = None
                for app in app_dict.keys():
                    if app in command_lower:
                        app_name = app
                        break
                
                if app_name:
                    path = app_dict[app_name]
                    try:
                        obj.launch_any_app(path)
                        return f"Launching {app_name}"
                    except Exception as e:
                        return f"Could not launch {app_name}: {str(e)}"
                else:
                    return "Please specify which application to launch"
            
            # Open website
            elif 'open' in command_lower and any(tld in command_lower for tld in ['.com', '.org', '.net', 'website']):
                domain = command_lower.split()[-1]
                try:
                    obj.website_opener(domain)
                    return f"Opening {domain}"
                except Exception as e:
                    return f"Could not open {domain}: {str(e)}"
            
            # YouTube video
            elif 'youtube' in command_lower:
                try:
                    video_query = command_lower.replace('youtube', '').replace('play', '').strip()
                    if video_query:
                        pywhatkit.playonyt(video_query)
                        return f"Playing {video_query} on YouTube"
                    else:
                        return "Please specify what to play on YouTube"
                except Exception as e:
                    return f"YouTube error: {str(e)}"
            
            # Send email
            elif 'email' in command_lower or 'send email' in command_lower:
                try:
                    sender_email = config.email
                    sender_password = config.email_password
                    
                    if sender_email == "<your_email>" or sender_password == "<your_email_password>":
                        return "Email configuration not set up. Please configure your email in config.py"
                    
                    speak("Whom do you want to email?")
                    recipient = obj.mic_input()
                    receiver_email = EMAIL_DIC.get(recipient.lower())
                    
                    if receiver_email:
                        speak("What is the subject?")
                        subject = obj.mic_input()
                        speak("What should I say?")
                        message = obj.mic_input()
                        
                        if subject and message:
                            msg = f'Subject: {subject}\n\n{message}'
                            obj.send_mail(sender_email, sender_password, receiver_email, msg)
                            return "Email sent successfully!"
                        else:
                            return "Email cancelled - missing subject or message"
                    else:
                        return "Recipient not found in contacts"
                        
                except Exception as e:
                    return f"Email error: {str(e)}"
            
            # Calculations
            elif any(word in command_lower for word in ['calculate', 'what is', 'who is']):
                return get_computational_intelligence_response(command)
            
            # Calendar events
            elif any(phrase in command_lower for phrase in CALENDAR_STRS):
                try:
                    obj.google_calendar_events(command)
                    return "Checking your calendar..."
                except Exception as e:
                    return f"Calendar error: {str(e)}"
            
            # Music control
            elif 'play music' in command_lower or 'hit some music' in command_lower:
                return "Music player feature needs to be configured with your music directory"
            
            # System information
            elif 'system' in command_lower:
                try:
                    sys_info = obj.system_info()
                    return sys_info
                except Exception as e:
                    return f"System info error: {str(e)}"
            
            # Location queries
            elif 'where is' in command_lower:
                place = command_lower.replace('where is', '').strip()
                if place:
                    try:
                        current_loc, target_loc, distance = obj.location(place)
                        return f"{place} is {distance} km away from your current location"
                    except Exception as e:
                        return f"Location error: {str(e)}"
                else:
                    return "Please specify a location"
            
            # IP address
            elif 'ip address' in command_lower:
                try:
                    ip = requests.get('https://api.ipify.org').text
                    return f"Your IP address is {ip}"
                except Exception as e:
                    return "Could not retrieve IP address"
            
            # Current location
            elif any(phrase in command_lower for phrase in ['where am i', 'current location', 'where i am']):
                try:
                    city, state, country = obj.my_location()
                    return f"You are currently in {city}, {state}, {country}"
                except Exception as e:
                    return "Could not determine current location"
            
            # Screenshot
            elif any(phrase in command_lower for phrase in ['take screenshot', 'capture screen']):
                try:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"jarvis_screenshot_{timestamp}.png"
                    img = pyautogui.screenshot()
                    img.save(filename)
                    return f"Screenshot saved as {filename}"
                except Exception as e:
                    return f"Screenshot error: {str(e)}"
            
            # File operations
            elif 'hide files' in command_lower:
                try:
                    os.system("attrib +h /s /d")
                    return "All files in current folder are now hidden"
                except Exception as e:
                    return f"File operation error: {str(e)}"
            
            elif 'show files' in command_lower or 'visible files' in command_lower:
                try:
                    os.system("attrib -h /s /d")
                    return "All files in current folder are now visible"
                except Exception as e:
                    return f"File operation error: {str(e)}"
            
            # Window switching
            elif 'switch window' in command_lower:
                try:
                    pyautogui.hotkey('alt', 'tab')
                    return "Switching window"
                except Exception as e:
                    return f"Window switching error: {str(e)}"
            
            # Goodbye
            elif any(word in command_lower for word in ['goodbye', 'offline', 'bye', 'exit', 'quit']):
                farewell = obj.language_support.get_template('goodbye')
                speak(farewell)
                self.stop()
                return farewell
            
            # Greeting responses
            elif command_lower in [greeting.lower() for greeting in GREETINGS]:
                return random.choice(GREETINGS_RES)
            
            # Default fallback
            else:
                suggestions = obj.get_context_suggestions(command)
                help_msg = "I didn't understand that command. "
                if suggestions:
                    help_msg += f"Did you mean: {', '.join(suggestions[:2])}? "
                help_msg += "Say 'help' to see all available commands."
                return help_msg
            
        except Exception as e:
            return obj.error_handler.handle_error('command_error', e, 'command_processing')

# ================================ ENHANCED GUI INTEGRATION ===========================================================================================================

class EnhancedMain(QMainWindow):
    """Enhanced main window with modern GUI"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_jarvis_thread()
    
    def init_ui(self):
        """Initialize the enhanced UI"""
        self.setWindowTitle("JARVIS Enhanced Assistant v3.0")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create modern GUI
        self.jarvis_gui = ModernJarvisGUI(obj.language_support)
        self.setCentralWidget(self.jarvis_gui)
        
        # Connect GUI signals
        self.jarvis_gui.start_btn.clicked.connect(self.start_jarvis)
        self.jarvis_gui.stop_btn.clicked.connect(self.stop_jarvis)
        
        # Status bar
        self.statusBar().showMessage("JARVIS Enhanced Assistant Ready")
        
        # Performance timer
        self.performance_timer = QTimer()
        self.performance_timer.timeout.connect(self.update_performance_stats)
        self.performance_timer.start(5000)  # Update every 5 seconds
    
    def setup_jarvis_thread(self):
        """Setup the JARVIS execution thread"""
        self.jarvis_thread = EnhancedMainThread()
        self.jarvis_thread.status_update.connect(self.update_status)
        self.jarvis_thread.command_processed.connect(self.on_command_processed)
        self.jarvis_thread.error_occurred.connect(self.on_error)
    
    def start_jarvis(self):
        """Start JARVIS execution"""
        if not self.jarvis_thread.isRunning():
            self.jarvis_thread.start()
            self.jarvis_gui.start_btn.setEnabled(False)
            self.jarvis_gui.stop_btn.setEnabled(True)
            self.jarvis_gui.status_widget.set_status("RUNNING", "#00ff41")
            self.statusBar().showMessage("JARVIS is listening...")
    
    def stop_jarvis(self):
        """Stop JARVIS execution"""
        if self.jarvis_thread.isRunning():
            self.jarvis_thread.stop()
            self.jarvis_thread.wait()
            self.jarvis_gui.start_btn.setEnabled(True)
            self.jarvis_gui.stop_btn.setEnabled(False)
            self.jarvis_gui.status_widget.set_status("STOPPED", "#ff4444")
            self.statusBar().showMessage("JARVIS stopped")
    
    def update_status(self, status):
        """Update status display"""
        self.jarvis_gui.status_widget.set_activity(status)
        self.statusBar().showMessage(status)
    
    def on_command_processed(self, command, response):
        """Handle processed commands"""
        self.jarvis_gui.append_to_display(f"👤 You: {command}")
        self.jarvis_gui.append_to_display(f"🤖 JARVIS: {response}")
        self.jarvis_gui.history_widget.add_command(command, response)
    
    def on_error(self, error_msg):
        """Handle errors"""
        self.jarvis_gui.append_to_display(f"❌ Error: {error_msg}")
        self.statusBar().showMessage(f"Error: {error_msg}")
    
    def update_performance_stats(self):
        """Update performance statistics"""
        try:
            stats = obj.get_performance_stats()
            
            # Update info display
            lang_info = stats['current_language']
            info_text = f"Language: {lang_info['name']}\n"
            info_text += f"Commands: {stats['commands_processed']}\n"
            info_text += f"Session: {stats['session_duration']}"
            
            self.jarvis_gui.info_text.setText(info_text)
            
        except Exception as e:
            print(f"Performance update error: {e}")
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.stop_jarvis()
        obj.cleanup()
        event.accept()

# ================================ MAIN EXECUTION ===========================================================================================================

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("JARVIS Enhanced Assistant")
    app.setApplicationVersion("3.0")
    app.setOrganizationName("JARVIS Systems")
    
    # Apply dark theme
    app.setStyle("Fusion")
    
    dark_palette = QtGui.QPalette()
    dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(255, 255, 255))
    dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
    dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(0, 0, 0))
    dark_palette.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor(255, 255, 255))
    dark_palette.setColor(QtGui.QPalette.Text, QtGui.QColor(255, 255, 255))
    dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(255, 255, 255))
    dark_palette.setColor(QtGui.QPalette.BrightText, QtGui.QColor(255, 0, 0))
    dark_palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(0, 0, 0))
    
    app.setPalette(dark_palette)
    
    # Create and show main window
    main_window = EnhancedMain()
    main_window.show()
    
    # Print startup information
    print("\n" + "="*60)
    print("🚀 JARVIS Enhanced Assistant v3.0")
    print("="*60)
    print("✨ Features:")
    print("  • Multi-language support (English, Hindi, Urdu, Arabic, and more)")
    print("  • Modern dark/light theme GUI")
    print("  • Enhanced voice recognition and TTS")
    print("  • Better performance with caching")
    print("  • Context-aware conversations")
    print("  • Enhanced error handling")
    print("  • Real-time voice visualization")
    print("  • Command history and suggestions")
    print("="*60)
    
    # Print performance info
    stats = obj.get_performance_stats()
    print(f"🌐 Current Language: {stats['current_language']['name']}")
    print(f"🎯 Ready for commands!")
    print("="*60)
    
    # Run the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()