
import os
import re
from typing import Dict, Optional

class MessageService:
    
    def __init__(self, properties_file: str = None):
        if properties_file is None:
            # Default to messages.properties in messages directory
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            properties_file = os.path.join(base_dir, 'messages', 'messages.properties')
        
        self.properties_file = properties_file
        self.messages: Dict[str, str] = {}
        self.load_messages()
    
    def load_messages(self):
        try:
            with open(self.properties_file, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse key=value pairs
                    if '=' in line:
                        key, value = line.split('=', 1)
                        self.messages[key.strip()] = value.strip()
        except FileNotFoundError:
            print(f"Warning: Messages file not found: {self.properties_file}")
        except Exception as e:
            print(f"Error loading messages: {e}")
    
    def get_message(self, key: str, *args, **kwargs) -> str:

        message = self.messages.get(key, key)
        
        try:
            # Handle both positional and keyword arguments
            if args:
                # Replace {0}, {1}, etc. with positional arguments
                for i, arg in enumerate(args):
                    message = message.replace(f'{{{i}}}', str(arg))
            
            if kwargs:
                # Replace {key} with keyword arguments
                for k, v in kwargs.items():
                    message = message.replace(f'{{{k}}}', str(v))
            
            return message
        except Exception as e:
            print(f"Error formatting message '{key}': {e}")
            return message
    
    def get_messages_for_prefix(self, prefix: str) -> Dict[str, str]:
        return {
            key: value for key, value in self.messages.items()
            if key.startswith(prefix)
        }
    
    def reload_messages(self):
        self.messages.clear()
        self.load_messages()
    
    def __call__(self, key: str, *args, **kwargs) -> str:
        return self.get_message(key, *args, **kwargs)

_message_service = None

def get_message_service() -> MessageService:
    global _message_service
    if _message_service is None:
        _message_service = MessageService()
    return _message_service

def msg(key: str, *args, **kwargs) -> str:
    return get_message_service().get_message(key, *args, **kwargs)

def reload_messages():
    global _message_service
    if _message_service:
        _message_service.reload_messages() 