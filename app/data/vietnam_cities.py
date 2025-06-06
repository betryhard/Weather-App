# Vietnamese Cities Database
# Major cities and provinces in Vietnam with coordinates

VIETNAM_CITIES = [
    # Major cities
    {"name": "Hà Nội", "lat": 21.0285, "lon": 105.8542, "region": "Miền Bắc"},
    {"name": "Thành phố Hồ Chí Minh", "lat": 10.8231, "lon": 106.6297, "region": "Miền Nam"},
    {"name": "Đà Nẵng", "lat": 16.0544, "lon": 108.2022, "region": "Miền Trung"},
    {"name": "Hải Phòng", "lat": 20.8449, "lon": 106.6881, "region": "Miền Bắc"},
    {"name": "Cần Thơ", "lat": 10.0452, "lon": 105.7469, "region": "Miền Nam"},
    
    # Northern provinces
    {"name": "Hạ Long", "lat": 20.9101, "lon": 107.1839, "region": "Quảng Ninh"},
    {"name": "Sapa", "lat": 22.3380, "lon": 103.8442, "region": "Lào Cai"},
    {"name": "Ninh Bình", "lat": 20.2506, "lon": 105.9744, "region": "Ninh Bình"},
    {"name": "Thái Nguyên", "lat": 21.5928, "lon": 105.8253, "region": "Thái Nguyên"},
    {"name": "Vĩnh Phúc", "lat": 21.3608, "lon": 105.6052, "region": "Vĩnh Phúc"},
    {"name": "Bắc Giang", "lat": 21.2731, "lon": 106.1946, "region": "Bắc Giang"},
    {"name": "Bắc Ninh", "lat": 21.1861, "lon": 106.0763, "region": "Bắc Ninh"},
    {"name": "Hải Dương", "lat": 20.9373, "lon": 106.3206, "region": "Hải Dương"},
    {"name": "Hưng Yên", "lat": 20.6464, "lon": 106.0512, "region": "Hưng Yên"},
    {"name": "Hà Nam", "lat": 20.5835, "lon": 105.9230, "region": "Hà Nam"},
    {"name": "Nam Định", "lat": 20.4341, "lon": 106.1675, "region": "Nam Định"},
    {"name": "Thái Bình", "lat": 20.4463, "lon": 106.3365, "region": "Thái Bình"},
    {"name": "Hòa Bình", "lat": 20.8156, "lon": 105.3388, "region": "Hòa Bình"},
    {"name": "Sơn La", "lat": 21.3256, "lon": 103.9188, "region": "Sơn La"},
    {"name": "Điện Biên Phủ", "lat": 21.3891, "lon": 103.0199, "region": "Điện Biên"},
    {"name": "Lào Cai", "lat": 22.4809, "lon": 103.9755, "region": "Lào Cai"},
    {"name": "Yên Bái", "lat": 21.7168, "lon": 104.8986, "region": "Yên Bái"},
    {"name": "Tuyên Quang", "lat": 21.8237, "lon": 105.2280, "region": "Tuyên Quang"},
    {"name": "Lạng Sơn", "lat": 21.8537, "lon": 106.7614, "region": "Lạng Sơn"},
    {"name": "Cao Bằng", "lat": 22.6356, "lon": 106.2595, "region": "Cao Bằng"},
    {"name": "Bắc Kạn", "lat": 22.1429, "lon": 105.8342, "region": "Bắc Kạn"},
    {"name": "Hà Giang", "lat": 22.8025, "lon": 104.9784, "region": "Hà Giang"},
    
    # Central provinces  
    {"name": "Huế", "lat": 16.4637, "lon": 107.5909, "region": "Thừa Thiên Huế"},
    {"name": "Quảng Nam", "lat": 15.5394, "lon": 108.0191, "region": "Quảng Nam"},
    {"name": "Hội An", "lat": 15.8801, "lon": 108.3380, "region": "Quảng Nam"},
    {"name": "Quảng Ngãi", "lat": 15.1214, "lon": 108.8044, "region": "Quảng Ngãi"},
    {"name": "Quy Nhon", "lat": 13.7563, "lon": 109.2297, "region": "Bình Định"},
    {"name": "Nha Trang", "lat": 12.2388, "lon": 109.1967, "region": "Khánh Hòa"},
    {"name": "Đà Lạt", "lat": 11.9404, "lon": 108.4583, "region": "Lâm Đồng"},
    {"name": "Phan Thiết", "lat": 10.9289, "lon": 108.1022, "region": "Bình Thuận"},
    {"name": "Vinh", "lat": 18.6792, "lon": 105.6811, "region": "Nghệ An"},
    {"name": "Hà Tĩnh", "lat": 18.3559, "lon": 105.8878, "region": "Hà Tĩnh"},
    {"name": "Đồng Hới", "lat": 17.4813, "lon": 106.5944, "region": "Quảng Bình"},
    {"name": "Tam Kỳ", "lat": 15.5736, "lon": 108.4736, "region": "Quảng Nam"},
    {"name": "Kon Tum", "lat": 14.3497, "lon": 108.0005, "region": "Kon Tum"},
    {"name": "Pleiku", "lat": 13.9833, "lon": 108.0167, "region": "Gia Lai"},
    {"name": "Buôn Ma Thuột", "lat": 12.6667, "lon": 108.0500, "region": "Đắk Lắk"},
    {"name": "Gia Nghĩa", "lat": 12.0049, "lon": 107.6925, "region": "Đắk Nông"},
    
    # Southern provinces
    {"name": "Vũng Tàu", "lat": 10.4113, "lon": 107.1362, "region": "Bà Rịa - Vũng Tàu"},
    {"name": "Biên Hòa", "lat": 10.9471, "lon": 106.8238, "region": "Đồng Nai"},
    {"name": "Thủ Dầu Một", "lat": 10.9804, "lon": 106.6519, "region": "Bình Dương"},
    {"name": "Tây Ninh", "lat": 11.3254, "lon": 106.0980, "region": "Tây Ninh"},
    {"name": "Long Xuyên", "lat": 10.3833, "lon": 105.4333, "region": "An Giang"},
    {"name": "Châu Đốc", "lat": 10.7008, "lon": 105.1158, "region": "An Giang"},
    {"name": "Mỹ Tho", "lat": 10.3596, "lon": 106.3560, "region": "Tiền Giang"},
    {"name": "Vĩnh Long", "lat": 10.2397, "lon": 105.9571, "region": "Vĩnh Long"},
    {"name": "Cao Lãnh", "lat": 10.4583, "lon": 105.6333, "region": "Đồng Tháp"},
    {"name": "Sa Đéc", "lat": 10.2958, "lon": 105.7572, "region": "Đồng Tháp"},
    {"name": "Bến Tre", "lat": 10.2415, "lon": 106.3759, "region": "Bến Tre"},
    {"name": "Trà Vinh", "lat": 9.9477, "lon": 106.3448, "region": "Trà Vinh"},
    {"name": "Sóc Trăng", "lat": 9.6003, "lon": 105.9800, "region": "Sóc Trăng"},
    {"name": "Bạc Liêu", "lat": 9.2836, "lon": 105.7244, "region": "Bạc Liêu"},
    {"name": "Cà Mau", "lat": 9.1526, "lon": 105.1524, "region": "Cà Mau"},
    {"name": "Rạch Giá", "lat": 10.0124, "lon": 105.0806, "region": "Kiên Giang"},
    {"name": "Hà Tiên", "lat": 10.3831, "lon": 104.4831, "region": "Kiên Giang"},
    {"name": "Phú Quốc", "lat": 10.2899, "lon": 103.9840, "region": "Kiên Giang"},
    
    # Additional cities and districts
    {"name": "Hưng Yên", "lat": 20.6464, "lon": 106.0512, "region": "Hưng Yên"},
    {"name": "Phú Lý", "lat": 20.5835, "lon": 105.9230, "region": "Hà Nam"},
    {"name": "Thanh Hóa", "lat": 19.8067, "lon": 105.7851, "region": "Thanh Hóa"},
    {"name": "Tam Điệp", "lat": 20.1542, "lon": 105.9058, "region": "Ninh Bình"},
    {"name": "Hạ Long Bay", "lat": 20.9101, "lon": 107.1839, "region": "Quảng Ninh"},
    {"name": "Cát Bà", "lat": 20.7333, "lon": 107.0500, "region": "Hải Phòng"},
]

def search_vietnam_cities(query, limit=10):
    if not query:
        return []
    
    query = query.lower().strip()
    results = []
    
    # Exact match first
    for city in VIETNAM_CITIES:
        city_name = city["name"].lower()
        if city_name == query:
            results.append(city)
    
    # Starts with match
    for city in VIETNAM_CITIES:
        city_name = city["name"].lower()
        if city_name.startswith(query) and city not in results:
            results.append(city)
    
    # Contains match
    for city in VIETNAM_CITIES:
        city_name = city["name"].lower()
        if query in city_name and city not in results:
            results.append(city)
    
    return results[:limit] 