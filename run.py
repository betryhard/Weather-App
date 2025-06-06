#!/usr/bin/env python3
"""
Simple Flask Hello World Application
"""

import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Create Flask application instance
app = create_app()

if __name__ == '__main__':
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000) 