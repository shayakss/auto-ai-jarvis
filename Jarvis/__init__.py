import speech_recognition as sr
import pyttsx3
import asyncio
import threading
import time
from datetime import datetime

from Jarvis.features import date_time
from Jarvis.features import launch_app
from Jarvis.features import website_open
from Jarvis.features import weather
from Jarvis.features import wikipedia
from Jarvis.features import news
from Jarvis.features import send_email
from Jarvis.features import google_search
from Jarvis.features import google_calendar
from Jarvis.features import note
from Jarvis.features import system_stats
from Jarvis.features import loc

# Import new enhanced features
from Jarvis.features.language_support import LanguageSupport
from Jarvis.features.performance_optimizer import PerformanceOptimizer
from Jarvis.features.enhanced_features import EnhancedErrorHandler, EnhancedVoiceCommands, ContextAwareProcessor


engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voices', voices[0].id)

class JarvisAssistant:
    def __init__(self):
        # Initialize enhanced features
        self.language_support = LanguageSupport()
        self.performance_optimizer = PerformanceOptimizer()
        self.error_handler = EnhancedErrorHandler(self.language_support)
        self.enhanced_commands = EnhancedVoiceCommands(self.error_handler)
        self.context_processor = ContextAwareProcessor()
        
        # Initialize performance optimization
        self.performance_optimizer.optimize_startup()
        
        # Performance metrics
        self.command_count = 0
        self.session_start_time = datetime.now()
        
        print("🚀 JARVIS Enhanced Assistant Initialized!")
        print(f"🌐 Language: {self.language_support.supported_languages[self.language_support.current_language]}")
        print("✨ All systems ready!")

    def mic_input(self):
        """
        Enhanced voice input with multi-language support and better error handling
        return: user's voice input as text if true, false if fail
        """
        try:
            # Use the enhanced voice recognition from language support
            command = self.language_support.listen()
            
            if command:
                self.command_count += 1
                print(f"🎤 Command #{self.command_count}: {command}")
                
                # Check for language change commands first
                lang_change_response = self.language_support.process_language_command(command)
                if lang_change_response:
                    self.tts(lang_change_response)
                    return command
                
                # Process with context awareness
                context_response = self.context_processor.process_with_context(command)
                if context_response:
                    return context_response
                
                return command
            else:
                error_msg = self.error_handler.handle_error('voice_error')
                self.tts(error_msg)
                return False
                
        except Exception as e:
            error_msg = self.error_handler.handle_error('voice_error', e)
            self.tts(error_msg)
            return False


    def tts(self, text):
        """
        Enhanced text-to-speech with multi-language support
        :param text: text(String)
        :return: True/False (Play sound if True otherwise write exception to log and return False)
        """
        try:
            # Use language-specific TTS
            self.language_support.speak(text)
            return True
        except Exception as e:
            error_msg = self.error_handler.handle_error('system_error', e)
            print(error_msg)
            return False

    def tell_me_date(self):

        return date_time.date()

    def tell_time(self):

        return date_time.time()

    def launch_any_app(self, path_of_app):
        """
        Launch any windows application 
        :param path_of_app: path of exe 
        :return: True is success and open the application, False if fail
        """
        return launch_app.launch_app(path_of_app)

    def website_opener(self, domain):
        """
        This will open website according to domain
        :param domain: any domain, example "youtube.com"
        :return: True if success, False if fail
        """
        return website_open.website_opener(domain)


    def weather(self, city):
        """
        Return weather with caching for better performance
        :param city: Any city of this world
        :return: weather info as string if True, or False
        """
        try:
            # Use cached response for better performance
            cache_key = f"weather_{city}"
            cached_result = self.performance_optimizer.cache.get(cache_key)
            
            if cached_result:
                print("📋 Using cached weather data")
                return cached_result
            
            # Fetch fresh weather data
            res = weather.fetch_weather(city)
            
            if res:
                # Cache the result
                self.performance_optimizer.cache.set(cache_key, res)
                
                # Translate if needed
                if self.language_support.current_language != 'en':
                    res = self.language_support.translate_text(res, self.language_support.current_language)
                
                return res
            else:
                return self.error_handler.handle_error('api_error')
                
        except Exception as e:
            return self.error_handler.handle_error('network_error', e)

    def tell_me(self, topic):
        """
        Tells about anything from wikipedia
        :param topic: any string is valid options
        :return: First 500 character from wikipedia if True, False if fail
        """
        return wikipedia.tell_me_about(topic)

    def news(self):
        """
        Fetch top news of the day from google news
        :return: news list of string if True, False if fail
        """
        return news.get_news()
    
    def send_mail(self, sender_email, sender_password, receiver_email, msg):

        return send_email.mail(sender_email, sender_password, receiver_email, msg)

    def google_calendar_events(self, text):
        service = google_calendar.authenticate_google()
        date = google_calendar.get_date(text) 
        
        if date:
            return google_calendar.get_events(date, service)
        else:
            pass
    
    def search_anything_google(self, command):
        google_search.google_search(command)

    def take_note(self, text):
        note.note(text)
    
    def system_info(self):
        return system_stats.system_stats()

    def location(self, location):
        current_loc, target_loc, distance = loc.loc(location)
        return current_loc, target_loc, distance

    def my_location(self):
        city, state, country = loc.my_location()
        return city, state, country
    
    # =================== NEW ENHANCED FEATURES ===================
    
    def process_enhanced_command(self, command):
        """
        Process commands using enhanced features
        """
        try:
            # Find matching enhanced command
            category, function = self.enhanced_commands.find_matching_command(command)
            
            if function:
                print(f"🎯 Processing {category} command: {command}")
                response = function(command)
                
                # Add to conversation history
                self.context_processor.add_to_history(command, response)
                
                return response
            
            # If no enhanced command found, return None to use traditional processing
            return None
            
        except Exception as e:
            return self.error_handler.handle_error('command_error', e)
    
    def get_help(self):
        """Get comprehensive help text"""
        return self.enhanced_commands.get_help_text()
    
    def change_language(self, language_code):
        """Change the assistant's language"""
        if self.language_support.set_language(language_code):
            lang_name = self.language_support.supported_languages[language_code]
            return self.language_support.get_template('language_changed', language=lang_name)
        return "Language not supported"
    
    def get_performance_stats(self):
        """Get performance statistics"""
        session_duration = datetime.now() - self.session_start_time
        
        stats = {
            'session_duration': str(session_duration),
            'commands_processed': self.command_count,
            'current_language': self.language_support.get_current_language_info(),
            'performance_report': self.performance_optimizer.get_performance_report(),
            'error_stats': self.error_handler.get_error_stats()
        }
        
        return stats
    
    def get_context_suggestions(self, current_input=""):
        """Get context-aware suggestions"""
        return self.context_processor.get_context_suggestions(current_input)
    
    def cleanup(self):
        """Clean up resources when shutting down"""
        self.performance_optimizer.cleanup()
        print("👋 JARVIS Enhanced Assistant shutting down gracefully...")
    
    def process_command_intelligently(self, command):
        """
        Main intelligent command processing with all enhancements
        """
        if not command:
            return self.error_handler.handle_error('voice_error')
        
        command = command.lower().strip()
        
        # Check for help request
        if command in ['help', 'what can you do', 'commands']:
            return self.get_help()
        
        # Check for enhanced commands first
        enhanced_response = self.process_enhanced_command(command)
        if enhanced_response:
            return enhanced_response
        
        # Traditional command processing with enhanced error handling
        try:
            # Date command
            if 'date' in command:
                result = self.tell_me_date()
                if self.language_support.current_language != 'en':
                    result = self.language_support.translate_text(result, self.language_support.current_language)
                return result
            
            # Time command
            elif 'time' in command:
                result = self.tell_time()
                template = self.language_support.get_template('time_response', time=result)
                return template
            
            # Weather command
            elif 'weather' in command:
                # Extract city from command
                words = command.split()
                city = words[-1] if len(words) > 1 else "London"
                return self.weather(city)
            
            # Wikipedia command
            elif 'tell me about' in command:
                topic = command.replace('tell me about', '').strip()
                result = self.tell_me(topic)
                if result and self.language_support.current_language != 'en':
                    result = self.language_support.translate_text(result, self.language_support.current_language)
                return result or self.language_support.get_template('not_found')
            
            # News command
            elif any(word in command for word in ['news', 'headlines', 'buzzing']):
                news_result = self.news()
                if news_result:
                    headlines = [article['title'] for article in news_result[:3]]  # Top 3 headlines
                    result = "Top headlines: " + ". ".join(headlines)
                    if self.language_support.current_language != 'en':
                        result = self.language_support.translate_text(result, self.language_support.current_language)
                    return result
                return self.error_handler.handle_error('api_error')
            
            # Default response for unrecognized commands
            else:
                return self.error_handler.handle_error('command_error')
                
        except Exception as e:
            return self.error_handler.handle_error('system_error', e, 'command_processing')
    
    # =================== LEGACY METHODS (UPDATED) ===================