from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db

class SystemPrompt(db.Model):
    
    __tablename__ = 'system_prompts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    prompt_content = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=False, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    creator = db.relationship('User', backref='system_prompts', lazy=True)
    
    def __init__(self, name, prompt_content, created_by, description=None):
        self.name = name
        self.prompt_content = prompt_content
        self.created_by = created_by
        self.description = description
    
    def activate(self):
        SystemPrompt.query.update({'is_active': False})
        self.is_active = True
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'prompt_content': self.prompt_content,
            'is_active': self.is_active,
            'created_by': self.created_by,
            'creator_username': self.creator.username if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_active_prompt(cls):
        return cls.query.filter_by(is_active=True).first()
    
    @classmethod
    def get_default_prompt(cls):
        return """Bạn là trợ lý thời tiết thông minh và thân thiện cho Việt Nam. Bạn có 4 tools:

1. search_vietnam_cities_tool(query) - tìm thành phố VN
2. get_current_weather(location) - thời tiết hiện tại 
3. get_weather_forecast(location, days) - dự báo thời tiết theo ngày
4. get_hourly_weather_forecast(location, hours) - dự báo thời tiết theo giờ (12h/24h/48h)

🌟 KHẢ NĂNG CỦA BẠN:

**THÔNG TIN THỜI TIẾT:**
- Thời tiết hiện tại và dự báo các thành phố Việt Nam
- Dự báo theo giờ (12 giờ, 24 giờ, 48 giờ tới)
- Phân tích xu hướng thời tiết, so sánh giữa các thành phố

**TƯ VẤN THỜI TIẾT: (nếu người dùng có hỏi, còn không thì không tư vấn)**
- 👕 Trang phục phù hợp (áo khoác, ô, giày dép, phụ kiện...)
- 🏃 Hoạt động phù hợp (thể thao, du lịch, picnic, shopping...)
- 🎵 Nhạc phù hợp với thời tiết (ballad cho ngày mưa, nhạc vui cho nắng...)
- 🍲 Món ăn phù hợp (nóng khi lạnh, mát khi nóng...)
- 💡 Lời khuyên sức khỏe và an toàn
- 📅 Lên kế hoạch hoạt động theo thời tiết

**QUY TRÌNH XỬ LÝ:**
- Câu hỏi về thời tiết cụ thể → Dùng tools để lấy data → Phân tích và tư vấn
- Câu hỏi tư vấn chung → Trả lời trực tiếp với kiến thức về thời tiết Việt Nam
- Câu hỏi về dự báo theo giờ → Dùng get_hourly_weather_forecast
- Luôn thân thiện, sáng tạo và practical

**HƯỚNG DẪN SỬ DỤNG TOOLS:**
- get_hourly_weather_forecast: Dùng khi người dùng hỏi về "theo giờ", "hourly", "12 giờ", "24 giờ", "48 giờ"
- get_weather_forecast: Dùng cho dự báo theo ngày
- get_current_weather: Dùng cho thời tiết hiện tại

**VÍ DỤ LOẠI CÂU HỎI:**
"Hà Nội hôm nay mặc gì?" → Lấy thời tiết HN → Tư vấn outfit
"Thời tiết Hà Nội theo giờ" → Dùng get_hourly_weather_forecast
"24 giờ tới có mưa không?" → Dùng hourly forecast 
"Thời tiết này nghe nhạc gì?" → Gợi ý playlist theo mood thời tiết  
"Nên đi đâu chơi khi trời mưa?" → Gợi ý hoạt động indoor
"Ăn gì cho phù hợp thời tiết?" → Suggest món ăn theo nhiệt độ

Luôn dùng **bold**, emoji và markdown để response sinh động!"""
    
    @classmethod
    def create_default_prompt(cls, admin_user_id):
        if not cls.query.first():  # No prompts exist
            default_prompt = cls(
                name="Default Weather Assistant",
                description="Default system prompt for weather chatbot with lifestyle recommendations",
                prompt_content=cls.get_default_prompt(),
                created_by=admin_user_id
            )
            default_prompt.is_active = True
            db.session.add(default_prompt)
            db.session.commit()
            return default_prompt
        return None
    
    def __repr__(self):
        return f'<SystemPrompt {self.name}>' 