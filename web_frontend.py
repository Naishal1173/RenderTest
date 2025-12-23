#!/usr/bin/env python3
"""
Gujarat Planning Regulation Assistant - Web Frontend
Expert AI assistant for NEW Gujarat-PART II PLANNING REGULATION
Provides accurate answers based on official regulation content
"""

from flask import Flask, render_template, request, jsonify
from robust_chatbot import RobustChatbot
import logging
import os
import socket

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize chatbot
chatbot = None

def initialize_chatbot():
    """Initialize the robust chatbot"""
    global chatbot
    try:
        chatbot = RobustChatbot()
        logger.info("✅ Robust chatbot initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize chatbot: {e}")
        return False

@app.route('/')
def home():
    """Home page with chat interface"""
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    """API endpoint to ask questions"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Please provide a question'
            })
        
        if not chatbot:
            return jsonify({
                'success': False,
                'error': 'Chatbot not initialized'
            })
        
        # Get answer from robust chatbot
        result = chatbot.ask(question)
        
        return jsonify({
            'success': True,
            'answer': result['answer']
        })
    
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while processing your question'
        })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'chatbot_ready': chatbot is not None,
        'service': 'Gujarat Planning Regulation Assistant'
    })

if __name__ == '__main__':
    print("🚀 Starting Gujarat Planning Regulation Assistant...")
    print("🏗️ Expert AI for Gujarat Planning Regulations")
    
    # Get port from environment (for deployment) or use 5000 for local
    port = int(os.environ.get('PORT', 5000))
    
    # Initialize chatbot
    if initialize_chatbot():
        print("✅ Chatbot initialized successfully")
        print(f"🌐 Web interface starting on port: {port}")
        
        # Get local IP for network access
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            print(f"🌐 Local access: http://localhost:{port}")
            print(f"📱 Network access: http://{local_ip}:{port}")
            print(f"🔗 Share this URL with others on your network!")
        except:
            print(f"🌐 Access at: http://localhost:{port}")
        
        app.run(debug=False, host='0.0.0.0', port=port)
    else:
        print("❌ Failed to initialize chatbot. Please check your data files.")
        exit(1)