from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import uuid
import json
import time
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Единое хранилище пользователей
users = {}  # key: device_id, value: user_data
messages = []

def generate_device_id():
    return str(uuid.uuid4())

def get_user_by_device_id(device_id):
    return users.get(device_id)

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/api/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        
        if not data or 'username' not in data:
            return jsonify({'error': 'Username is required'}), 400
        
        username = data['username'].strip()
        
        if not username:
            return jsonify({'error': 'Username cannot be empty'}), 400
        
        # Проверяем, нет ли пользователя с таким именем
        for user_data in users.values():
            if user_data['username'].lower() == username.lower():
                return jsonify({'error': 'Username already taken'}), 400
        
        # Генерация device ID
        device_id = generate_device_id()
        
        # Сохранение пользователя в ЕДИНОМ хранилище
        user_data = {
            'username': username,
            'device_id': device_id,
            'created_at': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat()
        }
        
        users[device_id] = user_data
        
        print(f"✅ New user registered: {username}")
        print(f"📱 Device ID: {device_id}")
        print(f"👥 Total users: {len(users)}")
        
        return jsonify({
            'message': 'User registered successfully',
            'device_id': device_id,
            'user': user_data
        }), 201
        
    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/send_message', methods=['POST'])
def send_message():
    try:
        data = request.get_json()
        
        if not data or 'device_id' not in data or 'message' not in data:
            return jsonify({'error': 'Device ID and message are required'}), 400
        
        device_id = data['device_id']
        message_text = data['message'].strip()
        
        if not message_text:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Проверка пользователя
        user = get_user_by_device_id(device_id)
        if not user:
            print(f"❌ Invalid device_id: {device_id}")
            print(f"📊 Available users: {list(users.keys())}")
            return jsonify({'error': 'Invalid device ID. Please register first.'}), 401
        
        # Создание сообщения
        message = {
            'id': len(messages) + 1,
            'device_id': device_id,
            'username': user['username'],
            'message': message_text,
            'timestamp': datetime.now().isoformat(),
            'time_display': datetime.now().strftime('%H:%M:%S')
        }
        
        messages.append(message)
        
        # Обновление времени последней активности
        user['last_seen'] = datetime.now().isoformat()
        
        print(f"💬 New message from {user['username']}: {message_text}")
        
        return jsonify({
            'message': 'Message sent successfully',
            'message_id': message['id']
        }), 201
        
    except Exception as e:
        print(f"❌ Send message error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/messages', methods=['GET'])
def get_messages():
    try:
        device_id = request.args.get('device_id')
        
        if not device_id:
            return jsonify({'error': 'Device ID is required'}), 400
        
        # Проверка пользователя
        user = get_user_by_device_id(device_id)
        if not user:
            print(f"❌ Get messages: Invalid device_id: {device_id}")
            return jsonify({'error': 'Invalid device ID'}), 401
        
        # Обновление времени последней активности
        user['last_seen'] = datetime.now().isoformat()
        
        return jsonify({
            'messages': messages,
            'total': len(messages)
        })
        
    except Exception as e:
        print(f"❌ Get messages error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/online_users', methods=['GET'])
def get_online_users():
    try:
        device_id = request.args.get('device_id')
        
        if not device_id:
            return jsonify({'error': 'Device ID is required'}), 400
        
        user = get_user_by_device_id(device_id)
        if not user:
            print(f"❌ Online users: Invalid device_id: {device_id}")
            print(f"📊 Available users: {list(users.keys())}")
            return jsonify({'error': 'Invalid device ID'}), 401
        
        # Обновление времени последней активности
        user['last_seen'] = datetime.now().isoformat()
        
        # Считаем пользователя онлайн, если он был активен в последние 5 минут
        now = datetime.now()
        online_users = []
        
        for user_data in users.values():
            last_seen = datetime.fromisoformat(user_data['last_seen'])
            if (now - last_seen).total_seconds() < 300:  # 5 минут
                online_users.append({
                    'username': user_data['username'],
                    'last_seen': user_data['last_seen']
                })
        
        print(f"👥 Online users request from {user['username']}")
        print(f"📊 Returning {len(online_users)} online users")
        
        return jsonify({
            'online_users': online_users,
            'total_online': len(online_users)
        })
        
    except Exception as e:
        print(f"❌ Get online users error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/debug/users', methods=['GET'])
def debug_users():
    """Отладочный endpoint для проверки пользователей"""
    return jsonify({
        'total_users': len(users),
        'users': users,
        'total_messages': len(messages)
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'OK',
        'timestamp': datetime.now().isoformat(),
        'total_users': len(users),
        'total_messages': len(messages)
    })

if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    print("🚀 Starting Flask Chat Server...")
    print("📍 Access: http://localhost:5000")
    print("🔧 Debug: http://localhost:5000/api/debug/users")
    app.run(debug=True, host='0.0.0.0', port=5000)