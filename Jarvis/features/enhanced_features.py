"""
Enhanced features for JARVIS with better error handling and new voice commands
"""

import os
import sys
import json
import re
import time
import random
import threading
import subprocess
import webbrowser
from datetime import datetime, timedelta
import requests
import psutil
from PIL import Image
import cv2
import numpy as np
import pyautogui
import speech_recognition as sr
from googletrans import Translator

class EnhancedErrorHandler:
    """Enhanced error handling with user-friendly messages"""
    
    def __init__(self, language_support=None):
        self.language_support = language_support
        self.error_log = []
        self.max_log_size = 100
        
        # Error messages in different languages
        self.error_messages = {
            'en': {
                'network_error': "I'm having trouble connecting to the internet. Please check your connection.",
                'api_error': "There was an issue with the service. Please try again later.",
                'file_error': "I couldn't access the file. Please check if it exists and you have permission.",
                'voice_error': "I couldn't understand what you said. Please speak clearly and try again.",
                'command_error': "I don't recognize that command. Say 'help' to see what I can do.",
                'system_error': "Something went wrong with the system. Please restart JARVIS.",
                'timeout_error': "The operation took too long. Please try again.",
                'permission_error': "I don't have permission to perform that action."
            },
            'hi': {
                'network_error': "मुझे इंटरनेट से जुड़ने में समस्या हो रही है। कृपया अपना कनेक्शन जांचें।",
                'api_error': "सेवा में कोई समस्या थी। कृपया बाद में पुनः प्रयास करें।",
                'file_error': "मैं फ़ाइल को एक्सेस नहीं कर सका। कृपया जांचें कि यह मौजूद है और आपके पास अनुमति है।",
                'voice_error': "मैं समझ नहीं सका कि आपने क्या कहा। कृपया स्पष्ट रूप से बोलें और पुनः प्रयास करें।",
                'command_error': "मैं उस कमांड को नहीं पहचानता। 'help' कहें कि मैं क्या कर सकता हूं।",
                'system_error': "सिस्टम में कुछ गड़बड़ हुई। कृपया JARVIS को रीस्टार्ट करें।",
                'timeout_error': "ऑपरेशन में बहुत समय लगा। कृपया पुनः प्रयास करें।",
                'permission_error': "मुझे वह क्रिया करने की अनुमति नहीं है।"
            },
            'ur': {
                'network_error': "مجھے انٹرنیٹ سے جڑنے میں دشواری ہو رہی ہے۔ برائے کرم اپنا کنکشن چیک کریں۔",
                'api_error': "سروس میں کوئی مسئلہ تھا۔ برائے کرم بعد میں دوبارہ کوشش کریں۔",
                'file_error': "میں فائل تک رسائی نہیں کر سکا۔ برائے کرم چیک کریں کہ یہ موجود ہے اور آپ کے پاس اجازت ہے۔",
                'voice_error': "میں سمجھ نہیں سکا کہ آپ نے کیا کہا۔ براہ کرم صاف بولیں اور دوبارہ کوشش کریں۔",
                'command_error': "میں اس کمانڈ کو نہیں پہچانتا۔ 'help' کہیں کہ میں کیا کر سکتا ہوں۔",
                'system_error': "سسٹم میں کچھ غلط ہوا۔ برائے کرم JARVIS کو دوبارہ شروع کریں۔",
                'timeout_error': "آپریشن میں بہت وقت لگا۔ برائے کرم دوبارہ کوشش کریں۔",
                'permission_error': "مجھے وہ عمل کرنے کی اجازت نہیں ہے۔"
            }
        }
    
    def handle_error(self, error_type, exception=None, context=None):
        """Handle errors with appropriate user messages"""
        # Log the error
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'exception': str(exception) if exception else None,
            'context': context
        }
        
        self.error_log.append(error_entry)
        
        # Limit log size
        if len(self.error_log) > self.max_log_size:
            self.error_log.pop(0)
        
        # Get appropriate language
        current_lang = 'en'
        if self.language_support:
            current_lang = self.language_support.current_language
        
        # Get error message
        messages = self.error_messages.get(current_lang, self.error_messages['en'])
        error_message = messages.get(error_type, messages['system_error'])
        
        print(f"ERROR: {error_message}")
        return error_message
    
    def get_error_stats(self):
        """Get error statistics"""
        if not self.error_log:
            return "No errors recorded."
        
        error_counts = {}
        for error in self.error_log:
            error_type = error['type']
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        return error_counts

class EnhancedVoiceCommands:
    """Enhanced voice commands with more functionality"""
    
    def __init__(self, error_handler=None):
        self.error_handler = error_handler
        self.translator = Translator()
        
        # Extended command patterns
        self.command_patterns = {
            'system_control': {
                'patterns': [
                    'shutdown', 'restart', 'sleep', 'hibernate', 'lock screen',
                    'show desktop', 'task manager', 'control panel'
                ],
                'function': self.handle_system_control
            },
            'media_control': {
                'patterns': [
                    'play music', 'pause music', 'stop music', 'next song', 'previous song',
                    'volume up', 'volume down', 'mute', 'unmute'
                ],
                'function': self.handle_media_control
            },
            'web_search': {
                'patterns': [
                    'search for', 'google', 'youtube search', 'wikipedia search',
                    'find information about', 'look up'
                ],
                'function': self.handle_web_search
            },
            'file_operations': {
                'patterns': [
                    'open file', 'create file', 'delete file', 'copy file',
                    'move file', 'rename file', 'show files'
                ],
                'function': self.handle_file_operations
            },
            'productivity': {
                'patterns': [
                    'set reminder', 'set alarm', 'schedule meeting',
                    'create task', 'add to calendar', 'take note'
                ],
                'function': self.handle_productivity
            },
            'entertainment': {
                'patterns': [
                    'tell joke', 'play game', 'random fact', 'quote of the day',
                    'riddle', 'story', 'poem'
                ],
                'function': self.handle_entertainment
            },
            'smart_home': {
                'patterns': [
                    'turn on lights', 'turn off lights', 'set temperature',
                    'close blinds', 'open blinds', 'lock doors', 'unlock doors'
                ],
                'function': self.handle_smart_home
            },
            'communication': {
                'patterns': [
                    'send message', 'make call', 'video call', 'send email',
                    'check messages', 'read messages'
                ],
                'function': self.handle_communication
            },
            'advanced_ai': {
                'patterns': [
                    'translate', 'summarize', 'explain', 'analyze',
                    'compare', 'recommend', 'predict'
                ],
                'function': self.handle_advanced_ai
            }
        }
    
    def find_matching_command(self, user_input):
        """Find matching command pattern"""
        user_input_lower = user_input.lower()
        
        for category, data in self.command_patterns.items():
            for pattern in data['patterns']:
                if pattern in user_input_lower:
                    return category, data['function']
        
        return None, None
    
    def handle_system_control(self, command):
        """Handle system control commands"""
        try:
            command_lower = command.lower()
            
            if 'shutdown' in command_lower:
                return self.confirm_action("Are you sure you want to shutdown?", 
                                         lambda: os.system("shutdown /s /t 1"))
            elif 'restart' in command_lower:
                return self.confirm_action("Are you sure you want to restart?", 
                                         lambda: os.system("shutdown /r /t 1"))
            elif 'sleep' in command_lower:
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                return "System going to sleep"
            elif 'lock screen' in command_lower:
                os.system("rundll32.exe user32.dll,LockWorkStation")
                return "Screen locked"
            elif 'show desktop' in command_lower:
                pyautogui.hotkey('win', 'd')
                return "Desktop shown"
            elif 'task manager' in command_lower:
                os.system("taskmgr")
                return "Task manager opened"
            elif 'control panel' in command_lower:
                os.system("control")
                return "Control panel opened"
            else:
                return "System command not recognized"
                
        except Exception as e:
            return self.error_handler.handle_error('system_error', e, 'system_control')
    
    def handle_media_control(self, command):
        """Handle media control commands"""
        try:
            command_lower = command.lower()
            
            if 'play' in command_lower:
                pyautogui.press('playpause')
                return "Playing media"
            elif 'pause' in command_lower:
                pyautogui.press('playpause')
                return "Media paused"
            elif 'stop' in command_lower:
                pyautogui.press('stop')
                return "Media stopped"
            elif 'next' in command_lower:
                pyautogui.press('nexttrack')
                return "Next track"
            elif 'previous' in command_lower:
                pyautogui.press('prevtrack')
                return "Previous track"
            elif 'volume up' in command_lower:
                pyautogui.press('volumeup')
                return "Volume increased"
            elif 'volume down' in command_lower:
                pyautogui.press('volumedown')
                return "Volume decreased"
            elif 'mute' in command_lower:
                pyautogui.press('volumemute')
                return "Audio muted"
            else:
                return "Media command not recognized"
                
        except Exception as e:
            return self.error_handler.handle_error('system_error', e, 'media_control')
    
    def handle_web_search(self, command):
        """Handle web search commands"""
        try:
            command_lower = command.lower()
            
            # Extract search query
            if 'search for' in command_lower:
                query = command_lower.split('search for', 1)[1].strip()
            elif 'google' in command_lower:
                query = command_lower.replace('google', '').strip()
            elif 'youtube search' in command_lower:
                query = command_lower.replace('youtube search', '').strip()
                webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
                return f"Searching YouTube for: {query}"
            elif 'wikipedia search' in command_lower:
                query = command_lower.replace('wikipedia search', '').strip()
                webbrowser.open(f"https://en.wikipedia.org/wiki/{query}")
                return f"Searching Wikipedia for: {query}"
            else:
                query = command_lower.replace('look up', '').replace('find information about', '').strip()
            
            if query:
                webbrowser.open(f"https://www.google.com/search?q={query}")
                return f"Searching Google for: {query}"
            else:
                return "Please specify what to search for"
                
        except Exception as e:
            return self.error_handler.handle_error('network_error', e, 'web_search')
    
    def handle_file_operations(self, command):
        """Handle file operations"""
        try:
            command_lower = command.lower()
            
            if 'open file' in command_lower:
                # Extract filename
                filename = command_lower.replace('open file', '').strip()
                if filename:
                    try:
                        os.startfile(filename)
                        return f"Opening file: {filename}"
                    except FileNotFoundError:
                        return f"File not found: {filename}"
                else:
                    return "Please specify the filename"
            
            elif 'show files' in command_lower:
                os.system("explorer")
                return "File explorer opened"
            
            elif 'create file' in command_lower:
                filename = command_lower.replace('create file', '').strip()
                if filename:
                    try:
                        with open(filename, 'w') as f:
                            f.write("")
                        return f"File created: {filename}"
                    except Exception as e:
                        return f"Error creating file: {str(e)}"
                else:
                    return "Please specify the filename"
            
            else:
                return "File operation not recognized"
                
        except Exception as e:
            return self.error_handler.handle_error('file_error', e, 'file_operations')
    
    def handle_productivity(self, command):
        """Handle productivity commands"""
        try:
            command_lower = command.lower()
            
            if 'set reminder' in command_lower:
                return "Reminder feature coming soon!"
            elif 'set alarm' in command_lower:
                return "Alarm feature coming soon!"
            elif 'take note' in command_lower:
                note_text = command_lower.replace('take note', '').strip()
                if note_text:
                    with open('jarvis_notes.txt', 'a') as f:
                        f.write(f"\n[{datetime.now()}] {note_text}")
                    return f"Note saved: {note_text}"
                else:
                    return "Please specify what to note"
            else:
                return "Productivity command not recognized"
                
        except Exception as e:
            return self.error_handler.handle_error('file_error', e, 'productivity')
    
    def handle_entertainment(self, command):
        """Handle entertainment commands"""
        try:
            command_lower = command.lower()
            
            if 'tell joke' in command_lower:
                jokes = [
                    "Why don't scientists trust atoms? Because they make up everything!",
                    "I told my wife she was drawing her eyebrows too high. She looked surprised.",
                    "Why don't programmers like nature? It has too many bugs!",
                    "I'm reading a book about anti-gravity. It's impossible to put down!",
                    "Why did the scarecrow win an award? He was outstanding in his field!"
                ]
                return random.choice(jokes)
            
            elif 'random fact' in command_lower:
                facts = [
                    "A group of flamingos is called a 'flamboyance'.",
                    "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old!",
                    "The human brain uses about 20% of the body's energy.",
                    "A day on Venus is longer than its year.",
                    "Bananas are berries, but strawberries aren't."
                ]
                return random.choice(facts)
            
            elif 'quote of the day' in command_lower:
                quotes = [
                    "The only way to do great work is to love what you do. - Steve Jobs",
                    "Innovation distinguishes between a leader and a follower. - Steve Jobs",
                    "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
                    "It is during our darkest moments that we must focus to see the light. - Aristotle",
                    "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill"
                ]
                return random.choice(quotes)
            
            elif 'riddle' in command_lower:
                riddles = [
                    "What has keys but no locks, space but no room, you can enter but not go inside? A keyboard!",
                    "What gets wetter the more it dries? A towel!",
                    "What has a head, a tail, is brown, and has no legs? A penny!",
                    "What can travel around the world while staying in a corner? A stamp!",
                    "What has many teeth but can't bite? A comb!"
                ]
                return random.choice(riddles)
            
            else:
                return "Entertainment command not recognized"
                
        except Exception as e:
            return self.error_handler.handle_error('system_error', e, 'entertainment')
    
    def handle_smart_home(self, command):
        """Handle smart home commands (placeholder)"""
        return "Smart home integration is not yet configured. Please set up your smart home devices first."
    
    def handle_communication(self, command):
        """Handle communication commands (placeholder)"""
        return "Communication features are coming soon!"
    
    def handle_advanced_ai(self, command):
        """Handle advanced AI commands"""
        try:
            command_lower = command.lower()
            
            if 'translate' in command_lower:
                # Extract text to translate
                text_to_translate = command_lower.replace('translate', '').strip()
                if text_to_translate:
                    try:
                        result = self.translator.translate(text_to_translate, dest='en')
                        return f"Translation: {result.text}"
                    except Exception as e:
                        return "Translation service unavailable"
                else:
                    return "Please specify text to translate"
            
            elif 'explain' in command_lower:
                topic = command_lower.replace('explain', '').strip()
                return f"I would explain {topic}, but my knowledge base is limited. Try searching online for detailed information."
            
            elif 'summarize' in command_lower:
                return "Text summarization feature coming soon!"
            
            else:
                return "Advanced AI command not recognized"
                
        except Exception as e:
            return self.error_handler.handle_error('api_error', e, 'advanced_ai')
    
    def confirm_action(self, message, action):
        """Confirm critical actions with user"""
        print(f"CONFIRMATION REQUIRED: {message}")
        # In a real implementation, this would wait for voice confirmation
        return "Action confirmation required. Feature coming soon!"
    
    def get_help_text(self):
        """Get help text for available commands"""
        help_text = """
        Available JARVIS Commands:
        
        🔧 System Control:
        • "shutdown" - Shutdown the computer
        • "restart" - Restart the computer
        • "sleep" - Put computer to sleep
        • "lock screen" - Lock the screen
        • "show desktop" - Show desktop
        • "task manager" - Open task manager
        
        🎵 Media Control:
        • "play music" - Play/pause media
        • "next song" - Next track
        • "previous song" - Previous track
        • "volume up/down" - Control volume
        • "mute" - Mute audio
        
        🌐 Web Search:
        • "search for [query]" - Google search
        • "youtube search [query]" - YouTube search
        • "wikipedia search [query]" - Wikipedia search
        
        📁 File Operations:
        • "open file [filename]" - Open file
        • "create file [filename]" - Create file
        • "show files" - Open file explorer
        
        📝 Productivity:
        • "take note [text]" - Save a note
        • "set reminder [text]" - Set reminder (coming soon)
        
        🎉 Entertainment:
        • "tell joke" - Random joke
        • "random fact" - Random fact
        • "quote of the day" - Inspirational quote
        • "riddle" - Brain teaser
        
        🧠 Advanced AI:
        • "translate [text]" - Translate text
        • "explain [topic]" - Explain topic
        
        Say "help" anytime to see this list!
        """
        return help_text

class ContextAwareProcessor:
    """Context-aware command processing"""
    
    def __init__(self):
        self.conversation_history = []
        self.current_context = None
        self.max_history = 10
    
    def add_to_history(self, user_input, response):
        """Add interaction to history"""
        self.conversation_history.append({
            'timestamp': datetime.now(),
            'user_input': user_input,
            'response': response
        })
        
        # Limit history size
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)
    
    def get_context_suggestions(self, current_input):
        """Get suggestions based on context"""
        if not self.conversation_history:
            return []
        
        # Simple context-based suggestions
        last_interaction = self.conversation_history[-1]
        
        suggestions = []
        
        # If last command was about weather, suggest related commands
        if 'weather' in last_interaction['user_input'].lower():
            suggestions.extend([
                "What's the weather like tomorrow?",
                "Weather forecast for this week",
                "Temperature in another city"
            ])
        
        # If last command was about time, suggest related commands
        elif 'time' in last_interaction['user_input'].lower():
            suggestions.extend([
                "What's the date?",
                "Set an alarm",
                "What time is it in another timezone?"
            ])
        
        return suggestions
    
    def process_with_context(self, user_input):
        """Process command with context awareness"""
        # Check for context-dependent commands
        if user_input.lower() in ['yes', 'no', 'okay', 'cancel']:
            if self.current_context:
                return self.handle_context_response(user_input)
        
        # Check for follow-up questions
        if user_input.lower().startswith(('and', 'also', 'then', 'what about')):
            return self.handle_follow_up(user_input)
        
        return None
    
    def handle_context_response(self, response):
        """Handle context-specific responses"""
        # Placeholder for context handling
        return f"Context response: {response}"
    
    def handle_follow_up(self, follow_up):
        """Handle follow-up questions"""
        # Placeholder for follow-up handling
        return f"Follow-up: {follow_up}"

# Example usage
if __name__ == "__main__":
    # Initialize components
    error_handler = EnhancedErrorHandler()
    voice_commands = EnhancedVoiceCommands(error_handler)
    context_processor = ContextAwareProcessor()
    
    # Test command processing
    test_commands = [
        "tell me a joke",
        "search for artificial intelligence",
        "what's the weather like",
        "open file test.txt",
        "translate hello world",
        "take note meeting at 3 PM"
    ]
    
    for command in test_commands:
        print(f"\nCommand: {command}")
        
        # Find matching command
        category, function = voice_commands.find_matching_command(command)
        
        if function:
            response = function(command)
            print(f"Response: {response}")
            
            # Add to context
            context_processor.add_to_history(command, response)
        else:
            print("Command not recognized")
    
    # Show help
    print("\n" + voice_commands.get_help_text())