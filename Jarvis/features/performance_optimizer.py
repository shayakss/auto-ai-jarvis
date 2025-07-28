"""
Performance optimization module for JARVIS
Handles caching, async operations, and response time improvements
"""

import asyncio
import threading
import time
import json
import os
import hashlib
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
import speech_recognition as sr
import queue

class CacheManager:
    """Manages caching for frequently accessed data"""
    
    def __init__(self, cache_dir="/tmp/jarvis_cache", max_size=100):
        self.cache_dir = cache_dir
        self.max_size = max_size
        self.cache = {}
        self.cache_times = {}
        self.cache_file = os.path.join(cache_dir, "cache.json")
        
        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)
        
        # Load existing cache
        self.load_cache()
    
    def _generate_key(self, data):
        """Generate cache key from data"""
        if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True)
        return hashlib.md5(str(data).encode()).hexdigest()
    
    def get(self, key, default=None):
        """Get cached value"""
        cache_key = self._generate_key(key)
        
        # Check if key exists and is not expired
        if cache_key in self.cache:
            cache_time = self.cache_times.get(cache_key)
            if cache_time and datetime.now() - cache_time < timedelta(hours=1):
                return self.cache[cache_key]
            else:
                # Remove expired cache
                self.remove(cache_key)
        
        return default
    
    def set(self, key, value, expire_hours=1):
        """Set cached value"""
        cache_key = self._generate_key(key)
        
        # Remove oldest cache if size limit exceeded
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache_times.keys(), key=lambda k: self.cache_times[k])
            self.remove(oldest_key)
        
        self.cache[cache_key] = value
        self.cache_times[cache_key] = datetime.now()
        
        # Save to file
        self.save_cache()
    
    def remove(self, key):
        """Remove cached value"""
        cache_key = self._generate_key(key)
        if cache_key in self.cache:
            del self.cache[cache_key]
            del self.cache_times[cache_key]
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        self.cache_times.clear()
        self.save_cache()
    
    def load_cache(self):
        """Load cache from file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    self.cache = data.get('cache', {})
                    # Convert timestamp strings back to datetime
                    for key, timestamp_str in data.get('cache_times', {}).items():
                        self.cache_times[key] = datetime.fromisoformat(timestamp_str)
        except Exception as e:
            print(f"Error loading cache: {e}")
    
    def save_cache(self):
        """Save cache to file"""
        try:
            # Convert datetime objects to strings for JSON serialization
            cache_times_str = {k: v.isoformat() for k, v in self.cache_times.items()}
            
            data = {
                'cache': self.cache,
                'cache_times': cache_times_str
            }
            
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")

class AsyncVoiceRecognizer:
    """Asynchronous voice recognition for better performance"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # Optimize recognizer settings
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
        
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.operation_timeout = 1
        self.recognizer.phrase_threshold = 0.3
    
    async def listen_continuously(self, callback=None):
        """Listen continuously for voice input"""
        self.is_listening = True
        
        def listen_worker():
            while self.is_listening:
                try:
                    with self.microphone as source:
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    
                    # Process audio in background
                    future = self.executor.submit(self._process_audio, audio)
                    result = future.result(timeout=10)
                    
                    if result and callback:
                        callback(result)
                        
                except sr.WaitTimeoutError:
                    pass
                except Exception as e:
                    print(f"Voice recognition error: {e}")
                    time.sleep(0.5)
        
        # Run in background thread
        thread = threading.Thread(target=listen_worker)
        thread.daemon = True
        thread.start()
        
        return thread
    
    def _process_audio(self, audio):
        """Process audio data"""
        try:
            # Use Google's speech recognition
            result = self.recognizer.recognize_google(audio, language='en-US')
            return result.lower()
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"Could not request results: {e}")
            return None
    
    async def listen_once(self, language='en-US', timeout=5):
        """Listen for a single command"""
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=5)
            
            # Process in background
            future = self.executor.submit(self._process_audio_with_language, audio, language)
            result = await asyncio.get_event_loop().run_in_executor(None, future.result, 10)
            
            return result
        except Exception as e:
            print(f"Single listen error: {e}")
            return None
    
    def _process_audio_with_language(self, audio, language):
        """Process audio with specific language"""
        try:
            result = self.recognizer.recognize_google(audio, language=language)
            return result.lower()
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"Could not request results: {e}")
            return None
    
    def stop_listening(self):
        """Stop continuous listening"""
        self.is_listening = False

class ResponseTimeOptimizer:
    """Optimizes response times for various operations"""
    
    def __init__(self):
        self.cache = CacheManager()
        self.response_times = {}
        
    def timed_operation(self, operation_name):
        """Decorator to measure operation time"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                
                response_time = end_time - start_time
                self.record_response_time(operation_name, response_time)
                
                return result
            return wrapper
        return decorator
    
    def record_response_time(self, operation, time_taken):
        """Record response time for analysis"""
        if operation not in self.response_times:
            self.response_times[operation] = []
        
        self.response_times[operation].append({
            'time': time_taken,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 100 entries
        if len(self.response_times[operation]) > 100:
            self.response_times[operation] = self.response_times[operation][-100:]
    
    def get_average_response_time(self, operation):
        """Get average response time for operation"""
        if operation not in self.response_times:
            return 0
        
        times = [entry['time'] for entry in self.response_times[operation]]
        return sum(times) / len(times) if times else 0
    
    def get_performance_stats(self):
        """Get overall performance statistics"""
        stats = {}
        for operation, times in self.response_times.items():
            time_values = [entry['time'] for entry in times]
            if time_values:
                stats[operation] = {
                    'average': sum(time_values) / len(time_values),
                    'min': min(time_values),
                    'max': max(time_values),
                    'count': len(time_values)
                }
        return stats

class PreloadManager:
    """Manages preloading of frequently used resources"""
    
    def __init__(self):
        self.preloaded_data = {}
        self.preload_tasks = []
    
    def preload_weather_data(self, cities):
        """Preload weather data for common cities"""
        from Jarvis.features import weather
        
        def preload_worker():
            for city in cities:
                try:
                    weather_data = weather.fetch_weather(city)
                    self.preloaded_data[f"weather_{city}"] = {
                        'data': weather_data,
                        'timestamp': datetime.now()
                    }
                except Exception as e:
                    print(f"Error preloading weather for {city}: {e}")
        
        thread = threading.Thread(target=preload_worker)
        thread.daemon = True
        thread.start()
        self.preload_tasks.append(thread)
    
    def preload_common_responses(self):
        """Preload common response templates"""
        common_responses = {
            'greeting': "Hello! How can I help you today?",
            'goodbye': "Goodbye! Have a great day!",
            'time': lambda: time.strftime("%H:%M:%S"),
            'date': lambda: time.strftime("%Y-%m-%d"),
            'help': "I can help you with weather, time, news, calculations, and much more!"
        }
        
        for key, response in common_responses.items():
            if callable(response):
                self.preloaded_data[key] = response()
            else:
                self.preloaded_data[key] = response
    
    def get_preloaded_data(self, key):
        """Get preloaded data if available"""
        data = self.preloaded_data.get(key)
        if data and isinstance(data, dict) and 'timestamp' in data:
            # Check if data is fresh (within 30 minutes)
            if datetime.now() - data['timestamp'] < timedelta(minutes=30):
                return data['data']
        return None

class ThreadPoolManager:
    """Manages thread pools for concurrent operations"""
    
    def __init__(self, max_workers=5):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.pending_tasks = {}
    
    def submit_task(self, task_id, func, *args, **kwargs):
        """Submit a task to the thread pool"""
        future = self.executor.submit(func, *args, **kwargs)
        self.pending_tasks[task_id] = future
        return future
    
    def get_task_result(self, task_id, timeout=None):
        """Get result of a submitted task"""
        if task_id in self.pending_tasks:
            future = self.pending_tasks[task_id]
            try:
                result = future.result(timeout=timeout)
                del self.pending_tasks[task_id]
                return result
            except Exception as e:
                del self.pending_tasks[task_id]
                raise e
        return None
    
    def cancel_task(self, task_id):
        """Cancel a pending task"""
        if task_id in self.pending_tasks:
            future = self.pending_tasks[task_id]
            future.cancel()
            del self.pending_tasks[task_id]
    
    def shutdown(self):
        """Shutdown the thread pool"""
        self.executor.shutdown(wait=True)

class PerformanceOptimizer:
    """Main performance optimization class"""
    
    def __init__(self):
        self.cache = CacheManager()
        self.voice_recognizer = AsyncVoiceRecognizer()
        self.response_optimizer = ResponseTimeOptimizer()
        self.preload_manager = PreloadManager()
        self.thread_pool = ThreadPoolManager()
        
        # Initialize preloading
        self.preload_manager.preload_common_responses()
        
        # Common cities for weather preloading
        common_cities = ['New York', 'London', 'Tokyo', 'Mumbai', 'Delhi', 'Karachi']
        self.preload_manager.preload_weather_data(common_cities)
    
    def optimize_startup(self):
        """Optimize application startup time"""
        print("🚀 Optimizing JARVIS startup...")
        
        # Preload essential components
        self.preload_manager.preload_common_responses()
        
        # Warm up voice recognition
        try:
            with sr.Microphone() as source:
                self.voice_recognizer.recognizer.adjust_for_ambient_noise(source, duration=0.5)
        except Exception as e:
            print(f"Voice recognition warmup error: {e}")
        
        print("✅ Startup optimization complete")
    
    def get_cached_response(self, command, func, *args, **kwargs):
        """Get cached response or execute function"""
        cache_key = f"{command}_{hash(str(args) + str(kwargs))}"
        
        # Check cache first
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Execute function and cache result
        result = func(*args, **kwargs)
        self.cache.set(cache_key, result)
        
        return result
    
    async def process_command_async(self, command, processor_func):
        """Process command asynchronously"""
        loop = asyncio.get_event_loop()
        
        # Submit to thread pool
        future = self.thread_pool.submit_task(
            f"command_{time.time()}",
            processor_func,
            command
        )
        
        # Wait for result
        result = await loop.run_in_executor(None, future.result, 10)
        return result
    
    def get_performance_report(self):
        """Get detailed performance report"""
        stats = self.response_optimizer.get_performance_stats()
        
        report = {
            'cache_stats': {
                'size': len(self.cache.cache),
                'hit_rate': 'N/A'  # Could be implemented
            },
            'response_times': stats,
            'preloaded_items': len(self.preload_manager.preloaded_data),
            'active_tasks': len(self.thread_pool.pending_tasks)
        }
        
        return report
    
    def cleanup(self):
        """Clean up resources"""
        self.voice_recognizer.stop_listening()
        self.thread_pool.shutdown()
        self.cache.save_cache()
        
        print("🧹 Performance optimizer cleaned up")

# Usage example and testing
if __name__ == "__main__":
    # Example usage
    optimizer = PerformanceOptimizer()
    
    # Test caching
    def expensive_operation(x):
        time.sleep(1)  # Simulate expensive operation
        return x * 2
    
    # First call - will be slow
    start = time.time()
    result1 = optimizer.get_cached_response("test", expensive_operation, 5)
    print(f"First call took: {time.time() - start:.2f}s")
    
    # Second call - will be fast (cached)
    start = time.time()
    result2 = optimizer.get_cached_response("test", expensive_operation, 5)
    print(f"Second call took: {time.time() - start:.2f}s")
    
    # Performance report
    report = optimizer.get_performance_report()
    print(f"Performance report: {report}")
    
    # Cleanup
    optimizer.cleanup()