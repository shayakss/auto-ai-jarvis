"""
Multi-language support for JARVIS Voice Assistant
Supports English, Hindi, Urdu, and other languages
"""

import json
import os
import subprocess
from googletrans import Translator
from langdetect import detect
import pyttsx3
import speech_recognition as sr

class LanguageSupport:
    def __init__(self):
        self.translator = Translator()
        self.current_language = 'en'  # Default English
        self.supported_languages = {
            'en': 'English',
            'hi': 'Hindi',
            'ur': 'Urdu',
            'ar': 'Arabic',
            'fr': 'French',
            'es': 'Spanish',
            'de': 'German',
            'it': 'Italian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese',
            'ru': 'Russian',
            'pt': 'Portuguese',
            'tr': 'Turkish',
            'bn': 'Bengali',
            'ta': 'Tamil',
            'te': 'Telugu',
            'ml': 'Malayalam',
            'mr': 'Marathi',
            'gu': 'Gujarati',
            'kn': 'Kannada',
            'pa': 'Punjabi'
        }
        
        # Language-specific voice recognition codes
        self.sr_language_codes = {
            'en': 'en-US',
            'hi': 'hi-IN',
            'ur': 'ur-PK',
            'ar': 'ar-SA',
            'fr': 'fr-FR',
            'es': 'es-ES',
            'de': 'de-DE',
            'it': 'it-IT',
            'ja': 'ja-JP',
            'ko': 'ko-KR',
            'zh': 'zh-CN',
            'ru': 'ru-RU',
            'pt': 'pt-BR',
            'tr': 'tr-TR',
            'bn': 'bn-BD',
            'ta': 'ta-IN',
            'te': 'te-IN',
            'ml': 'ml-IN',
            'mr': 'mr-IN',
            'gu': 'gu-IN',
            'kn': 'kn-IN',
            'pa': 'pa-IN'
        }
        
        # Load language templates
        self.templates = self.load_language_templates()
        
        # Initialize TTS engine (gracefully handle headless environments)
        try:
            # Check if on Windows
            if os.name == 'nt':
                self.tts_engine = pyttsx3.init()
                self.setup_tts_for_language(self.current_language)
                self.tts_available = True
            else:
                # On Linux/Unix systems, use espeak if available
                try:
                    subprocess.run(['espeak', '--version'], capture_output=True, check=True)
                    self.tts_engine = None  # We'll use espeak directly
                    self.tts_available = True
                    self.use_espeak = True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    print("TTS not available on this system (neither Windows SAPI nor espeak found)")
                    self.tts_engine = None
                    self.tts_available = False
                    self.use_espeak = False
        except Exception as e:
            print(f"TTS initialization failed: {e}")
            self.tts_engine = None
            self.tts_available = False
            self.use_espeak = False
    
    def load_language_templates(self):
        """Load language-specific response templates"""
        templates = {
            'en': {
                'greeting': "Hello! How can I help you today?",
                'goodbye': "Goodbye! Have a great day!",
                'error': "Sorry, I couldn't understand that. Please try again.",
                'listening': "I'm listening...",
                'processing': "Processing your request...",
                'time_response': "The current time is {time}",
                'date_response': "Today's date is {date}",
                'weather_response': "The weather in {city} is {weather}",
                'not_found': "Sorry, I couldn't find that information.",
                'task_completed': "Task completed successfully!",
                'language_changed': "Language changed to {language}",
                'help': "I can help you with time, weather, news, calculations, and much more. Just ask me!"
            },
            'hi': {
                'greeting': "नमस्ते! आज मैं आपकी कैसे सहायता कर सकता हूं?",
                'goodbye': "अलविदा! आपका दिन शुभ हो!",
                'error': "क्षमा करें, मैं इसे समझ नहीं सका। कृपया पुनः प्रयास करें।",
                'listening': "मैं सुन रहा हूं...",
                'processing': "आपका अनुरोध प्रसंस्करण कर रहा हूं...",
                'time_response': "वर्तमान समय {time} है",
                'date_response': "आज की तारीख {date} है",
                'weather_response': "{city} में मौसम {weather} है",
                'not_found': "क्षमा करें, मुझे वह जानकारी नहीं मिली।",
                'task_completed': "कार्य सफलतापूर्वक पूरा हुआ!",
                'language_changed': "भाषा {language} में बदल गई",
                'help': "मैं समय, मौसम, समाचार, गणना और बहुत कुछ में आपकी मदद कर सकता हूं। बस मुझसे पूछें!"
            },
            'ur': {
                'greeting': "السلام علیکم! آج میں آپ کی کیسے مدد کر سکتا ہوں؟",
                'goodbye': "خدا حافظ! آپ کا دن اچھا گزرے!",
                'error': "معذرت، میں اسے سمجھ نہیں سکا۔ براہ کرم دوبارہ کوشش کریں۔",
                'listening': "میں سن رہا ہوں...",
                'processing': "آپ کی درخواست پر کارروائی کر رہا ہوں...",
                'time_response': "موجودہ وقت {time} ہے",
                'date_response': "آج کی تاریخ {date} ہے",
                'weather_response': "{city} میں موسم {weather} ہے",
                'not_found': "معذرت، مجھے یہ معلومات نہیں مل سکیں۔",
                'task_completed': "کام کامیابی سے مکمل ہوا!",
                'language_changed': "زبان {language} میں تبدیل ہو گئی",
                'help': "میں وقت، موسم، خبریں، حساب کتاب اور بہت کچھ میں آپ کی مدد کر سکتا ہوں۔ بس مجھ سے پوچھیں!"
            }
        }
        return templates
    
    def detect_language(self, text):
        """Detect the language of input text"""
        try:
            detected_lang = detect(text)
            return detected_lang if detected_lang in self.supported_languages else 'en'
        except:
            return 'en'  # Default to English if detection fails
    
    def translate_text(self, text, target_lang='en', source_lang='auto'):
        """Translate text from source language to target language"""
        try:
            if source_lang == target_lang:
                return text
            
            result = self.translator.translate(text, src=source_lang, dest=target_lang)
            return result.text
        except Exception as e:
            print(f"Translation error: {e}")
            return text
    
    def set_language(self, language_code):
        """Set the current language"""
        if language_code in self.supported_languages:
            self.current_language = language_code
            self.setup_tts_for_language(language_code)
            return True
        return False
    
    def setup_tts_for_language(self, language_code):
        """Setup text-to-speech for specific language"""
        try:
            voices = self.tts_engine.getProperty('voices')
            
            # Language-specific voice selection
            language_voice_map = {
                'en': ['english', 'en-us', 'en-gb'],
                'hi': ['hindi', 'hi-in'],
                'ur': ['urdu', 'ur-pk'],
                'ar': ['arabic', 'ar-sa'],
                'fr': ['french', 'fr-fr'],
                'es': ['spanish', 'es-es'],
                'de': ['german', 'de-de'],
                'it': ['italian', 'it-it'],
                'ja': ['japanese', 'ja-jp'],
                'ko': ['korean', 'ko-kr'],
                'zh': ['chinese', 'zh-cn'],
                'ru': ['russian', 'ru-ru'],
                'pt': ['portuguese', 'pt-br'],
                'tr': ['turkish', 'tr-tr']
            }
            
            preferred_voices = language_voice_map.get(language_code, ['english'])
            
            # Find appropriate voice
            selected_voice = None
            if voices:
                for voice in voices:
                    voice_name = voice.name.lower()
                    voice_lang = voice.languages[0].lower() if voice.languages else ""
                    
                    for preferred in preferred_voices:
                        if preferred in voice_name or preferred in voice_lang:
                            selected_voice = voice
                            break
                    
                    if selected_voice:
                        break
                
                if selected_voice:
                    self.tts_engine.setProperty('voice', selected_voice.id)
                elif voices:
                    # Use default voice if no specific language voice found
                    self.tts_engine.setProperty('voice', voices[0].id)
            
            # Set speech rate and volume
            self.tts_engine.setProperty('rate', 175)
            self.tts_engine.setProperty('volume', 0.9)
            
        except Exception as e:
            print(f"TTS setup error (this may be normal in headless environments): {e}")
    
    def speak(self, text, language=None):
        """Speak text in the specified language"""
        try:
            if not self.tts_available:
                print(f"🔊 TTS: {text}")
                return
            
            if hasattr(self, 'use_espeak') and self.use_espeak:
                # Use espeak for Linux systems
                try:
                    lang_code = language or self.current_language
                    espeak_lang = {
                        'en': 'en',
                        'hi': 'hi',
                        'ur': 'ur',
                        'ar': 'ar',
                        'fr': 'fr',
                        'es': 'es',
                        'de': 'de',
                        'it': 'it',
                        'ja': 'ja',
                        'ko': 'ko',
                        'zh': 'zh',
                        'ru': 'ru',
                        'pt': 'pt',
                        'tr': 'tr'
                    }.get(lang_code, 'en')
                    
                    subprocess.run(['espeak', '-v', espeak_lang, text], 
                                 capture_output=True, timeout=10)
                    return
                except Exception as e:
                    print(f"Espeak error: {e}")
                    print(f"🔊 TTS: {text}")
                    return
            
            # Use pyttsx3 for Windows
            if self.tts_engine:
                if language and language != self.current_language:
                    self.setup_tts_for_language(language)
                
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            else:
                print(f"🔊 TTS: {text}")
                
        except Exception as e:
            print(f"Speech error (printing instead): {text}")
            print(f"   Error details: {e}")
    
    def listen(self, language_code=None):
        """Listen for voice input in specified language"""
        try:
            # In headless environments, simulate voice input
            if os.getenv('DISPLAY') is None:
                print("🎤 Voice input simulation (headless environment)")
                return None
            
            r = sr.Recognizer()
            lang_code = language_code or self.current_language
            sr_lang = self.sr_language_codes.get(lang_code, 'en-US')
            
            with sr.Microphone() as source:
                print(f"Listening in {self.supported_languages[lang_code]}...")
                r.adjust_for_ambient_noise(source, duration=1)
                r.energy_threshold = 4000
                audio = r.listen(source, timeout=5)
            
            print("Recognizing...")
            command = r.recognize_google(audio, language=sr_lang).lower()
            print(f"You said: {command}")
            return command
            
        except sr.UnknownValueError:
            error_msg = self.get_template('error')
            print(error_msg)
            return None
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            return None
        except Exception as e:
            print(f"Listening error: {e}")
            return None
    
    def get_template(self, template_key, **kwargs):
        """Get language-specific template with formatting"""
        templates = self.templates.get(self.current_language, self.templates['en'])
        template = templates.get(template_key, templates.get('error'))
        
        try:
            return template.format(**kwargs)
        except KeyError:
            return template
    
    def get_available_languages(self):
        """Get list of available languages"""
        return [(code, name) for code, name in self.supported_languages.items()]
    
    def process_language_command(self, command):
        """Process language change commands"""
        command_lower = command.lower()
        
        # English commands
        if any(phrase in command_lower for phrase in ['change language', 'switch language', 'language to']):
            # Extract language from command
            for code, name in self.supported_languages.items():
                if name.lower() in command_lower:
                    old_lang = self.current_language
                    if self.set_language(code):
                        msg = self.get_template('language_changed', language=name)
                        return msg
            return "Language not supported or not found in command"
        
        # Hindi commands
        elif any(phrase in command_lower for phrase in ['भाषा बदलें', 'भाषा बदलो', 'भाषा']):
            # Similar logic for Hindi
            pass
        
        # Urdu commands
        elif any(phrase in command_lower for phrase in ['زبان تبدیل کریں', 'زبان']):
            # Similar logic for Urdu
            pass
        
        return None
    
    def get_current_language_info(self):
        """Get current language information"""
        return {
            'code': self.current_language,
            'name': self.supported_languages[self.current_language]
        }