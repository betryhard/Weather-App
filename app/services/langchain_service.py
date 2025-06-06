import os
import json
from typing import Dict, List, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from app.services.weather_service import WeatherService
from app.data.vietnam_cities import search_vietnam_cities
from app.models.system_prompt import SystemPrompt

weather_service = WeatherService()

@tool
def search_vietnam_cities_tool(query: str, limit: int = 5) -> str:
    """Tìm kiếm thành phố Việt Nam theo tên hoặc từ khóa.
    
    Args:
        query: Tên thành phố hoặc từ khóa tìm kiếm (ví dụ: "hà nội", "tp hcm", "đà nẵng")
        limit: Số lượng kết quả trả về tối đa (mặc định 5)
    
    Returns:
        Chuỗi JSON chứa danh sách thành phố tìm được với thông tin chi tiết
    """
    try:
        found_cities = search_vietnam_cities(query.lower(), limit)
        
        if not found_cities:
            return json.dumps({
                "found": False,
                "message": "Không tìm thấy thành phố nào khớp với từ khóa này trong Việt Nam"
            }, ensure_ascii=False, indent=2)
        
        result = {
            "found": True,
            "cities": []
        }
        
        for city in found_cities:
            city_mapping = {
                'Hà Nội': 'Hanoi',
                'Thành phố Hồ Chí Minh': 'Ho Chi Minh City',
                'Đà Nẵng': 'Da Nang',
                'Hải Phòng': 'Hai Phong',
                'Cần Thơ': 'Can Tho',
                'Huế': 'Hue',
                'Nha Trang': 'Nha Trang',
                'Đà Lạt': 'Da Lat',
                'Vũng Tàu': 'Vung Tau',
                'Phú Quốc': 'Phu Quoc',
                'Hạ Long': 'Ha Long',
                'Sapa': 'Sapa',
                'Hội An': 'Hoi An'
            }
            
            english_name = city_mapping.get(city['name'], city['name'])
            
            result["cities"].append({
                "vietnamese_name": city['name'],
                "english_name": english_name,
                "region": city['region'],
                "coordinates": {
                    "lat": city['lat'],
                    "lon": city['lon']
                }
            })
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({
            "found": False,
            "error": f"Lỗi khi tìm kiếm: {str(e)}"
        }, ensure_ascii=False, indent=2)

@tool
def get_current_weather(location: str) -> str:
    """Lấy thông tin thời tiết hiện tại của một địa điểm cụ thể.
    
    Args:
        location: Tên thành phố bằng tiếng Anh (ví dụ: "Hanoi", "Ho Chi Minh City", "Da Nang")
    
    Returns:
        Chuỗi JSON chứa thông tin thời tiết hiện tại hoặc thông báo lỗi
    """
    try:
        result = weather_service.get_current_weather(location)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Lỗi khi lấy thời tiết: {str(e)}"

@tool  
def get_weather_forecast(location: str, days: int = 3) -> str:
    """Lấy dự báo thời tiết cho vài ngày tới của một địa điểm.
    
    Args:
        location: Tên thành phố bằng tiếng Anh (ví dụ: "Hanoi", "Ho Chi Minh City", "Da Nang") 
        days: Số ngày dự báo (tối đa 5 ngày)
    
    Returns:
        Chuỗi JSON chứa dự báo thời tiết hoặc thông báo lỗi
    """
    try:
        if days > 5:
            days = 5
        result = weather_service.get_forecast(location, days)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Lỗi khi lấy dự báo: {str(e)}"

@tool
def get_hourly_weather_forecast(location: str, hours: int = 24) -> str:
    """Lấy dự báo thời tiết theo giờ cho một địa điểm cụ thể.
    
    Args:
        location: Tên thành phố bằng tiếng Anh (ví dụ: "Hanoi", "Ho Chi Minh City", "Da Nang")
        hours: Số giờ dự báo (12, 24, hoặc 48 giờ)
    
    Returns:
        Chuỗi JSON chứa dự báo thời tiết theo giờ hoặc thông báo lỗi
    """
    try:
        # Validate hours parameter
        if hours not in [12, 24, 48]:
            hours = 24
        
        result = weather_service.get_hourly_forecast_by_location(location, hours)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Lỗi khi lấy dự báo theo giờ: {str(e)}"

class WeatherChatbotService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=self.api_key,
            temperature=0.6 # small halucination, more concise answers
        )
        
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self):
        try:
            active_prompt = SystemPrompt.get_active_prompt()
            if active_prompt:
                print(f"Loading system prompt from database: {active_prompt.name}")
                return active_prompt.prompt_content
            else:
                print("No active system prompt found in database, using default")
                return SystemPrompt.get_default_prompt()
        except Exception as e:
            print(f"Error loading system prompt from database: {e}")
            # Fallback to default prompt
            return SystemPrompt.get_default_prompt()
    
    def reload_system_prompt(self):
        self.system_prompt = self._load_system_prompt()

    def chat(self, message: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        try:
            print(f"System prompt: {self.system_prompt}")
            
            messages = [SystemMessage(content=self.system_prompt)]
            
            if conversation_history:
                for item in conversation_history[-6:]:  
                    if item.get('type') == 'human' and item.get('content'):
                        content = item['content'].strip()
                        if content:  
                            messages.append(HumanMessage(content=content))
                    elif item.get('type') == 'ai' and item.get('content'):
                        content = item['content'].strip()
                        if content:  
                            messages.append(AIMessage(content=content))
            
            messages.append(HumanMessage(content=message))
            
            llm_with_tools = self.llm.bind_tools([
                search_vietnam_cities_tool,
                get_current_weather, 
                get_weather_forecast,
                get_hourly_weather_forecast
            ])
            
            response = llm_with_tools.invoke(messages)
            
            if hasattr(response, 'tool_calls') and response.tool_calls:
                all_tool_results = []
                city_found = None
                
                for tool_call in response.tool_calls:
                    try:
                        if tool_call['name'] == 'search_vietnam_cities_tool':
                            result = search_vietnam_cities_tool.invoke(tool_call['args'])
                            all_tool_results.append(f"Kết quả tìm kiếm thành phố: {result}")
                            
                            try:
                                city_data = json.loads(result)
                                if city_data.get('found') and city_data.get('cities'):
                                    city_found = city_data['cities'][0]['english_name']
                            except:
                                pass
                                
                        elif tool_call['name'] == 'get_current_weather':
                            result = get_current_weather.invoke(tool_call['args'])
                            all_tool_results.append(f"Thời tiết hiện tại: {result}")
                        elif tool_call['name'] == 'get_weather_forecast':
                            result = get_weather_forecast.invoke(tool_call['args'])
                            all_tool_results.append(f"Dự báo thời tiết: {result}")
                        elif tool_call['name'] == 'get_hourly_weather_forecast':
                            result = get_hourly_weather_forecast.invoke(tool_call['args'])
                            all_tool_results.append(f"Dự báo thời tiết theo giờ: {result}")
                    except Exception as tool_error:
                        print(f"Tool call error: {tool_error}")
                        all_tool_results.append(f"Lỗi khi thực hiện: {str(tool_error)}")
                
                if city_found and not any('Thời tiết hiện tại:' in result or 'Dự báo thời tiết:' in result or 'Dự báo thời tiết theo giờ:' in result for result in all_tool_results):
                    try:
                        if any(keyword in message.lower() for keyword in ['theo giờ', 'hourly', 'mỗi giờ', '12 giờ', '24 giờ', '48 giờ']):
                            # Determine hours based on message
                            hours = 24
                            if '12 giờ' in message.lower() or '12h' in message.lower():
                                hours = 12
                            elif '48 giờ' in message.lower() or '48h' in message.lower():
                                hours = 48
                            
                            weather_result = get_hourly_weather_forecast.invoke({"location": city_found, "hours": hours})
                            all_tool_results.append(f"Dự báo thời tiết theo giờ: {weather_result}")
                        elif any(keyword in message.lower() for keyword in ['dự báo', 'forecast', 'ngày tới', 'tuần']):
                            weather_result = get_weather_forecast.invoke({"location": city_found, "days": 3})
                            all_tool_results.append(f"Dự báo thời tiết: {weather_result}")
                        else:
                            weather_result = get_current_weather.invoke({"location": city_found})
                            all_tool_results.append(f"Thời tiết hiện tại: {weather_result}")
                    except Exception as auto_error:
                        print(f"Auto weather call error: {auto_error}")
                        all_tool_results.append(f"Lỗi khi lấy thời tiết: {str(auto_error)}")
                
                if all_tool_results:
                    enhanced_message = f"""
Người dùng hỏi: {message}

Dữ liệu từ hệ thống:
{chr(10).join(all_tool_results)}

Hãy phân tích dữ liệu trên và trả lời câu hỏi của người dùng một cách thân thiện, chi tiết bằng tiếng Việt. Sử dụng markdown formatting với **bold** cho thông tin quan trọng.
"""
                    
                    final_messages = [
                        SystemMessage(content=self.system_prompt),
                        HumanMessage(content=enhanced_message)
                    ]
                    
                    final_response = self.llm.invoke(final_messages)
                    
                    return {
                        'success': True,
                        'message': final_response.content,
                        'has_tool_calls': True
                    }
            
            return {
                'success': True,
                'message': response.content,
                'has_tool_calls': False
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error in WeatherChatbotService.chat: {error_msg}")
            
            return {
                'success': False,
                'error': f"Đã xảy ra lỗi: {error_msg}",
                'message': "Xin lỗi, tôi đang gặp sự cố kỹ thuật. Vui lòng thử lại sau."
            }
    
    def get_weather_suggestions(self) -> List[str]:
        try:
            llm_suggestions = self._generate_weather_questions_with_llm()
            if llm_suggestions:
                return llm_suggestions
        except Exception as e:
            print(f"Error generating LLM suggestions: {e}")
        
        return [
            "Thời tiết Hà Nội hôm nay thế nào?",
            "Dự báo thời tiết TP Hồ Chí Minh 3 ngày tới",
            "Nhiệt độ hiện tại ở Đà Nẵng là bao nhiêu?", 
            "Thời tiết Nha Trang có mưa không?",
            "Dự báo thời tiết Đà Lạt tuần này",
            "Thời tiết Hà Nội theo giờ trong 24 giờ tới",
            "Dự báo 12 giờ tới ở TP Hồ Chí Minh"
        ]
    
    def _generate_weather_questions_with_llm(self) -> List[str]:
        try:
            popular_cities = [
                'Hà Nội', 'TP Hồ Chí Minh', 'Đà Nẵng', 'Huế', 'Nha Trang', 
                'Đà Lạt', 'Vũng Tàu', 'Phú Quốc', 'Hạ Long', 'Sapa', 
                'Hội An', 'Cần Thơ', 'Hải Phòng', 'Quy Nhon', 'Phan Thiết'
            ]
            
            prompt = f"""Tạo ra 5 câu hỏi gợi ý về thời tiết bằng tiếng Việt. Yêu cầu:

1. Mỗi câu hỏi phải khác nhau và thú vị
2. Sử dụng các thành phố Việt Nam: {', '.join(popular_cities)}
3. Đa dạng về loại câu hỏi: thời tiết hiện tại, dự báo, lời khuyên, so sánh
4. Ngôn ngữ tự nhiên, thân thiện
5. Trả về chính xác 5 câu, mỗi câu một dòng, không có số thứ tự

Ví dụ format:
Thời tiết Hà Nội hôm nay có mưa không?
Nên mang áo khoác khi đi Đà Lạt không?

Tạo 5 câu hỏi mới, đa dạng và thú vị:"""

            messages = [
                SystemMessage(content="Bạn là trợ lý tạo câu hỏi gợi ý về thời tiết. Tạo câu hỏi ngắn gọn, tự nhiên và thú vị."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            questions = []
            lines = response.content.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith(('1.', '2.', '3.', '4.', '5.')):
                    line = line.lstrip('- • * ')
                    if line and '?' in line: 
                        questions.append(line)
                elif line and any(line.startswith(f'{i}.') for i in range(1, 6)):
                    clean_line = line.split('.', 1)[1].strip()
                    if clean_line and '?' in clean_line:
                        questions.append(clean_line)
            
            if len(questions) >= 5:
                return questions[:5]
            elif len(questions) > 0:
                fallback_questions = [
                    "Thời tiết hôm nay có phù hợp để đi dạo không?",
                    "Tuần này có nên mang ô theo không?",
                    "Thời tiết cuối tuần sẽ như thế nào?",
                    "Hôm nay có nên mặc áo khoác không?",
                    "Thời tiết có phù hợp để đi picnic không?"
                ]
                
                while len(questions) < 5 and fallback_questions:
                    questions.append(fallback_questions.pop(0))
                
                return questions[:5]
            
            return None  
            
        except Exception as e:
            print(f"Error in _generate_weather_questions_with_llm: {e}")
            return None
    
    def get_vietnam_city_suggestions(self) -> List[Dict[str, str]]:
        from app.data.vietnam_cities import VIETNAM_CITIES
        
        popular_cities = [
            'Hà Nội', 'Thành phố Hồ Chí Minh', 'Đà Nẵng', 'Huế', 
            'Nha Trang', 'Đà Lạt', 'Vũng Tàu', 'Phú Quốc', 
            'Hạ Long', 'Sapa', 'Hội An', 'Cần Thơ'
        ]
        
        suggestions = []
        for city_data in VIETNAM_CITIES:
            if city_data['name'] in popular_cities:
                suggestions.append({
                    'name': city_data['name'],
                    'region': city_data['region'],
                    'coordinates': f"{city_data['lat']}, {city_data['lon']}"
                })
        
        return suggestions[:12]  
    
    def search_vietnamese_cities_for_chat(self, query: str, limit: int = 5) -> List[Dict[str, str]]:
        found_cities = search_vietnam_cities(query, limit)
        
        return [{
            'name': city['name'],
            'region': city['region'],
            'suggestion': f"Thời tiết {city['name']} hôm nay thế nào?"
        } for city in found_cities]
    
    def refresh_weather_suggestions(self) -> List[str]:
        """Tạo mới 5 câu hỏi gợi ý về thời tiết từ LLM"""
        return self._generate_weather_questions_with_llm() or self.get_weather_suggestions()
    
    def get_contextual_weather_suggestions(self, current_location: str = None) -> List[str]:
        """Tạo câu hỏi gợi ý có context về địa điểm hiện tại"""
        try:
            if not current_location:
                current_location = "Việt Nam"
            
            prompt = f"""Tạo ra 5 câu hỏi gợi ý về thời tiết bằng tiếng Việt, tập trung vào {current_location}. Yêu cầu:

1. Ít nhất 2-3 câu hỏi liên quan đến {current_location}
2. Các câu còn lại về thời tiết tổng quát hoặc thành phố khác
3. Đa dạng: thời tiết hiện tại, dự báo, lời khuyên, hoạt động
4. Ngôn ngữ tự nhiên, thân thiện
5. Mỗi câu một dòng, không số thứ tự

Ví dụ với Hà Nội:
Thời tiết Hà Nội hôm nay có mưa không?
Nên mang áo gì khi ra đường ở Hà Nội?
So sánh thời tiết Hà Nội và TP Hồ Chí Minh?

Tạo 5 câu hỏi cho {current_location}:"""

            messages = [
                SystemMessage(content="Bạn là trợ lý tạo câu hỏi gợi ý về thời tiết có context địa điểm."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            questions = []
            lines = response.content.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith(('1.', '2.', '3.', '4.', '5.')):
                    line = line.lstrip('- • * ')
                    if line and '?' in line:
                        questions.append(line)
                elif line and any(line.startswith(f'{i}.') for i in range(1, 6)):
                    clean_line = line.split('.', 1)[1].strip()
                    if clean_line and '?' in clean_line:
                        questions.append(clean_line)
            
            if len(questions) >= 5:
                return questions[:5]
            else:
                return self.get_weather_suggestions()
                
        except Exception as e:
            print(f"Error in get_contextual_weather_suggestions: {e}")
            return self.get_weather_suggestions() 