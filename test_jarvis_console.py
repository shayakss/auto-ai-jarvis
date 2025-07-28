"""
Test JARVIS Enhanced Assistant - Console Version
This tests the core functionality without GUI
"""

import sys
import time
from datetime import datetime

try:
    from Jarvis import JarvisAssistant
    print("✅ Successfully imported JarvisAssistant")
except Exception as e:
    print(f"❌ Error importing JarvisAssistant: {e}")
    sys.exit(1)

def test_jarvis_features():
    """Test various JARVIS features"""
    print("\n" + "="*60)
    print("🚀 JARVIS Enhanced Assistant - Console Test")
    print("="*60)
    
    # Initialize JARVIS
    try:
        jarvis = JarvisAssistant()
        print("✅ JARVIS initialization successful!")
    except Exception as e:
        print(f"❌ JARVIS initialization failed: {e}")
        return
    
    # Test language support
    print(f"\n🌐 Current Language: {jarvis.language_support.get_current_language_info()['name']}")
    print(f"🗣️ Supported Languages: {len(jarvis.language_support.supported_languages)} languages")
    
    # Test basic features
    print("\n📋 Testing Core Features:")
    
    # Test date and time
    try:
        current_time = jarvis.tell_time()
        current_date = jarvis.tell_me_date()
        print(f"⏰ Current Time: {current_time}")
        print(f"📅 Current Date: {current_date}")
    except Exception as e:
        print(f"❌ Time/Date error: {e}")
    
    # Test TTS
    try:
        print("🔊 Testing Text-to-Speech...")
        greeting = jarvis.language_support.get_template('greeting')
        print(f"   Speaking: {greeting}")
        jarvis.tts(greeting)
        time.sleep(2)  # Give TTS time to finish
        print("✅ TTS test completed")
    except Exception as e:
        print(f"❌ TTS error: {e}")
    
    # Test enhanced commands
    print("\n🎯 Testing Enhanced Commands:")
    
    test_commands = [
        "tell joke",
        "what's the time",
        "help",
        "random fact"
    ]
    
    for command in test_commands:
        try:
            print(f"\n👤 Command: {command}")
            response = jarvis.process_command_intelligently(command)
            print(f"🤖 Response: {response}")
            
            if response and "joke" not in command.lower():  # Don't speak jokes in console test
                jarvis.tts(response[:50] + "..." if len(response) > 50 else response)
                time.sleep(1)
                
        except Exception as e:
            print(f"❌ Command error: {e}")
    
    # Test language switching
    print("\n🌍 Testing Language Support:")
    try:
        # Get available languages
        languages = jarvis.language_support.get_available_languages()[:3]  # Test first 3
        
        for code, name in languages:
            if code != 'en':  # Don't test English as it's default
                print(f"\n🔄 Switching to {name} ({code})")
                result = jarvis.change_language(code)
                print(f"   Result: {result}")
                
                # Test greeting in new language
                greeting = jarvis.language_support.get_template('greeting')
                print(f"   Greeting: {greeting}")
                
                # Switch back to English
                jarvis.change_language('en')
                
    except Exception as e:
        print(f"❌ Language switching error: {e}")
    
    # Test performance stats
    print("\n📊 Testing Performance Stats:")
    try:
        stats = jarvis.get_performance_stats()
        print(f"   Session Duration: {stats['session_duration']}")
        print(f"   Commands Processed: {stats['commands_processed']}")
        print(f"   Current Language: {stats['current_language']['name']}")
    except Exception as e:
        print(f"❌ Performance stats error: {e}")
    
    # Test caching
    print("\n💾 Testing Caching System:")
    try:
        # Test with a weather query (if API key is configured)
        cache_test_key = "test_cache_key"
        test_data = "This is test cached data"
        
        # Set cache
        jarvis.performance_optimizer.cache.set(cache_test_key, test_data)
        
        # Get from cache
        cached_result = jarvis.performance_optimizer.cache.get(cache_test_key)
        
        if cached_result == test_data:
            print("✅ Cache system working correctly")
        else:
            print("❌ Cache system not working correctly")
            
    except Exception as e:
        print(f"❌ Caching error: {e}")
    
    # Test error handling
    print("\n🛡️ Testing Error Handling:")
    try:
        error_msg = jarvis.error_handler.handle_error('test_error', None, 'testing')
        print(f"   Error Handler Response: {error_msg}")
        print("✅ Error handling working correctly")
    except Exception as e:
        print(f"❌ Error handling error: {e}")
    
    # Cleanup
    try:
        jarvis.cleanup()
        print("\n🧹 Cleanup completed successfully")
    except Exception as e:
        print(f"❌ Cleanup error: {e}")
    
    print("\n" + "="*60)
    print("🎉 JARVIS Enhanced Assistant Test Completed!")
    print("="*60)

def interactive_test():
    """Interactive testing mode"""
    print("\n🎮 Interactive Testing Mode")
    print("Type 'exit' to quit, 'help' for commands")
    print("-" * 40)
    
    try:
        jarvis = JarvisAssistant()
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                print("🤖 Processing...")
                response = jarvis.process_command_intelligently(user_input)
                print(f"🤖 JARVIS: {response}")
                
                # Optional: Speak the response (commented out for console testing)
                # jarvis.tts(response)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        jarvis.cleanup()
        
    except Exception as e:
        print(f"❌ Interactive test error: {e}")

def main():
    """Main test function"""
    print("JARVIS Enhanced Assistant - Test Suite")
    print("Select test mode:")
    print("1. Automated Feature Test")
    print("2. Interactive Test")
    print("3. Both")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            test_jarvis_features()
        elif choice == '2':
            interactive_test()
        elif choice == '3':
            test_jarvis_features()
            print("\n" + "="*60)
            interactive_test()
        else:
            print("Invalid choice. Running automated test...")
            test_jarvis_features()
            
    except KeyboardInterrupt:
        print("\n👋 Test interrupted. Goodbye!")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    main()