from flask import Blueprint, render_template, request, jsonify, session, current_app
from flask_login import login_required, current_user
from app.utils.messages import msg
import json
import os
import traceback

# Create Blueprint
chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

# Global variables for chatbot service
chatbot_service = None
chatbot_error = None

def reset_chatbot_service():
    global chatbot_service, chatbot_error
    chatbot_service = None
    chatbot_error = None

def reload_chatbot_system_prompt():
    global chatbot_service
    if chatbot_service is not None:
        try:
            chatbot_service.reload_system_prompt()
            return True
        except Exception as e:
            print(f"Error reloading system prompt: {e}")
            return False
    return False

def init_chatbot_service():
    global chatbot_service, chatbot_error
    
    if chatbot_service is not None:
        return chatbot_service
        
    try:
        current_app.logger.info("Initializing chatbot service...")
        
        if not os.getenv('GEMINI_API_KEY'):
            chatbot_error = msg('chatbot.error.api_key_missing')
            current_app.logger.warning(f"Chatbot initialization failed: {chatbot_error}")
            return None
        
        current_app.logger.info("GEMINI_API_KEY found, importing services...")
        
        try:
            from app.services.langchain_service import WeatherChatbotService
            current_app.logger.info("WeatherChatbotService imported successfully")
            
            chatbot_service = WeatherChatbotService()
            current_app.logger.info("WeatherChatbotService initialized successfully")
            return chatbot_service
            
        except ImportError as ie:
            chatbot_error = msg('chatbot.error.service_error', str(ie))
            current_app.logger.error(f"Import error when initializing chatbot: {ie}")
            current_app.logger.error(traceback.format_exc())
            return None
            
        except Exception as se:
            chatbot_error = msg('chatbot.error.service_error', str(se))
            current_app.logger.error(f"Service error when initializing chatbot: {se}")
            current_app.logger.error(traceback.format_exc())
            return None
            
    except Exception as e:
        chatbot_error = msg('chatbot.error.service_error', str(e))
        current_app.logger.error(f"Critical error when initializing chatbot: {e}")
        current_app.logger.error(traceback.format_exc())
        return None

@chatbot_bp.route('/')
@login_required
def index():
    try:
        current_app.logger.info(f"Chatbot index accessed by user: {current_user.username}")
        
        service = init_chatbot_service()
        
        
        suggestions = []
        if service:
            try:
                suggestions = service.get_weather_suggestions()
                current_app.logger.info(f"Got {len(suggestions)} suggestions")
            except Exception as e:
                current_app.logger.error(f"Error getting suggestions: {e}")
        
        api_status = {
            'gemini_configured': bool(os.getenv('GEMINI_API_KEY')),
            'weather_configured': bool(os.getenv('OPENWEATHERMAP_API_KEY')),
            'chatbot_ready': service is not None,
            'error_message': chatbot_error
        }
        
        current_app.logger.info(f"API Status: {api_status}")
        
        return render_template('chatbot/index.html', 
                             title=msg('chatbot.title'),
                             suggestions=suggestions,
                             api_status=api_status)
                             
    except Exception as e:
        current_app.logger.error(f"Error in chatbot index: {e}")
        current_app.logger.error(traceback.format_exc())
        return render_template('chatbot/index.html', 
                             title=msg('chatbot.title'),
                             suggestions=[],
                             api_status={'chatbot_ready': False, 'error_message': str(e)})

@chatbot_bp.route('/chat', methods=['POST'])
@login_required  
def chat():
    try:
        current_app.logger.info(f"Chat request from user: {current_user.username}")
        
        # Log request data
        current_app.logger.info(f"Request content type: {request.content_type}")
        current_app.logger.info(f"Request data: {request.data}")
        
        data = request.get_json()
        current_app.logger.info(f"Parsed JSON data: {data}")
        
        if not data or 'message' not in data:
            current_app.logger.warning("No message in request data")
            return jsonify({
                'success': False,
                'error': msg('chatbot.error.no_message')
            }), 400
        
        user_message = data['message'].strip()
        current_app.logger.info(f"User message: '{user_message}'")
        
        if not user_message:
            current_app.logger.warning("Empty message")
            return jsonify({
                'success': False,
                'error': msg('chatbot.error.empty_message')
            }), 400
        
        gemini_key = os.getenv('GEMINI_API_KEY')
        current_app.logger.info(f"GEMINI_API_KEY present: {bool(gemini_key)}")
        if gemini_key:
            current_app.logger.info(f"GEMINI_API_KEY length: {len(gemini_key)}")
        
        if not gemini_key:
            current_app.logger.warning("GEMINI_API_KEY not configured")
            return jsonify({
                'success': False,
                'error': msg('chatbot.error.api_key_not_configured'),
                'message': msg('chatbot.message.api_key_configure')
            }), 503
        
        service = init_chatbot_service()
        
        current_app.logger.info(f"Chatbot service available: {service is not None}")
        current_app.logger.info(f"Chatbot error: {chatbot_error}")
        
        if not service:
            current_app.logger.error(f"Chatbot service not available: {chatbot_error}")
            return jsonify({
                'success': False,
                'error': chatbot_error or msg('chatbot.error.service_unavailable'),
                'message': msg('chatbot.message.service_issue')
            }), 503
        
        chat_history = session.get('chat_history', [])
        current_app.logger.info(f"Chat history length: {len(chat_history)}")
        
        current_app.logger.info("Calling chatbot service...")
        try:
            response = service.chat(user_message, chat_history)
            current_app.logger.info(f"Chatbot response: {response}")
        except Exception as chat_error:
            current_app.logger.error(f"Error calling chatbot service: {chat_error}")
            current_app.logger.error(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': msg('chatbot.error.service_error', str(chat_error)),
                'message': msg('chatbot.message.service_call_error')
            }), 500
        
        if response['success']:
            current_app.logger.info("Chatbot response successful")
            
            chat_history.append({
                'type': 'human',
                'content': user_message,
                'timestamp': None
            })
            chat_history.append({
                'type': 'ai', 
                'content': response['message'],
                'timestamp': None
            })
            
            if len(chat_history) > 20:
                chat_history = chat_history[-20:]
            
            session['chat_history'] = chat_history
            current_app.logger.info("Chat history updated")
            
            return jsonify({
                'success': True,
                'message': response['message'],
                'has_tool_calls': response.get('has_tool_calls', False)
            })
        else:
            current_app.logger.warning(f"Chatbot response failed: {response}")
            error_msg = response.get('error', '')
            if 'API_KEY_INVALID' in error_msg or 'API key not valid' in error_msg:
                current_app.logger.error("Invalid Gemini API key")
                return jsonify({
                    'success': False,
                    'error': msg('chatbot.error.api_key_invalid'),
                    'message': msg('chatbot.message.api_key_invalid_detailed')
                }), 401
            else:
                return jsonify({
                    'success': False,
                    'error': response.get('error', msg('chatbot.error.unknown')),
                    'message': response.get('message', msg('chatbot.message.cannot_answer'))
                }), 500
            
    except Exception as e:
        current_app.logger.error(f"Critical error in chat endpoint: {e}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': msg('chatbot.message.server_error', str(e)),
            'message': msg('chatbot.error.unexpected')
        }), 500

@chatbot_bp.route('/clear', methods=['POST'])
@login_required
def clear_chat():
    try:
        session.pop('chat_history', None)
        return jsonify({'success': True, 'message': msg('chatbot.message.history_cleared')})
    except Exception as e:
        current_app.logger.error(f"Error clearing chat: {e}")
        return jsonify({
            'success': False, 
            'error': msg('chatbot.error.clear_history', str(e))
        }), 500

@chatbot_bp.route('/suggestions')
@login_required
def get_suggestions():
    try:
        service = init_chatbot_service()
        suggestions = []
        if service:
            suggestions = service.get_weather_suggestions()
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
    except Exception as e:
        current_app.logger.error(f"Error getting suggestions: {e}")
        return jsonify({
            'success': False,
            'error': msg('chatbot.error.get_suggestions', str(e))
        }), 500

@chatbot_bp.route('/history')
@login_required
def get_history():
    try:
        chat_history = session.get('chat_history', [])
        return jsonify({
            'success': True,
            'history': chat_history
        })
    except Exception as e:
        current_app.logger.error(f"Error getting chat history: {e}")
        return jsonify({
            'success': False,
            'error': msg('chatbot.error.get_history', str(e))
        }), 500

@chatbot_bp.route('/status')
@login_required
def get_status():
    try:
        service = init_chatbot_service()
        status = {
            'gemini_configured': bool(os.getenv('GEMINI_API_KEY')),
            'weather_configured': bool(os.getenv('OPENWEATHERMAP_API_KEY')),
            'chatbot_ready': service is not None,
            'error_message': chatbot_error
        }
        
        current_app.logger.info(f"Status check: {status}")
        
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        current_app.logger.error(f"Error checking status: {e}")
        return jsonify({
            'success': False,
            'error': msg('chatbot.error.check_status', str(e))
        }), 500 