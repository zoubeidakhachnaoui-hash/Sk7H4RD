#!/usr/bin/env python3
"""
PANEL FF - Premium VIP Services
Direct API integration for player info
Outfit script integrated directly
Developed by H4RDIXX OFFICIAL AND SK7 D5M
"""

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import hashlib
import time
import os
import json
from datetime import datetime
import secrets
import asyncio
import traceback
import requests
from PIL import Image
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
VIP_USERS_FILE = os.path.join(BASE_DIR, 'vip_users.json')
STATS_FILE = os.path.join(BASE_DIR, 'stats_data.json')
os.chdir(BASE_DIR)

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

outfit_executor = ThreadPoolExecutor(max_workers=10)

TOKEN_ROTATION_TIME = 18000
last_token_time = time.time()
current_token = None
vip_sessions = {}

def load_vip_users():
    if os.path.exists(VIP_USERS_FILE):
        try:
            with open(VIP_USERS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"admin": {"password": "vip123", "created": "System", "active": True}}

def save_vip_users(users):
    with open(VIP_USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def load_stats():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        "website_visits": 0,
        "unique_visitors": [],
        "telegram_bot_users": [],
        "telegram_commands_count": 0,
        "dance_commands": 0,
        "last_updated": ""
    }

def save_stats(stats):
    stats['last_updated'] = datetime.now().isoformat()
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)

def track_visitor(ip_address):
    stats = load_stats()
    stats['website_visits'] += 1
    if ip_address and ip_address not in stats['unique_visitors']:
        stats['unique_visitors'].append(ip_address)
    save_stats(stats)
    return stats

def validate_vip_user(username, password):
    users = load_vip_users()
    if username in users:
        user_data = users[username]
        if isinstance(user_data, dict):
            # Check if account is expired
            expires_at = user_data.get('expires_at')
            if expires_at:
                from datetime import datetime
                try:
                    expire_date = datetime.strptime(expires_at, '%Y-%m-%d %H:%M')
                    if datetime.now() > expire_date:
                        # Account expired, deactivate it
                        user_data['active'] = False
                        save_vip_users(users)
                        return False
                except:
                    pass
            if not user_data.get('active', True):
                return False
    if username in users:
        user = users[username]
        if isinstance(user, dict):
            return user.get('password') == password and user.get('active', True)
        else:
            return user == password
    return False

def generate_token():
    current_hour_block = int(time.time() / TOKEN_ROTATION_TIME)
    token_string = f"FFBot_SecureAPI_{current_hour_block}_sk7"
    return hashlib.sha256(token_string.encode()).hexdigest()

def get_current_token():
    global current_token, last_token_time
    current_time = time.time()
    if current_token is None or (current_time - last_token_time) > TOKEN_ROTATION_TIME:
        current_token = generate_token()
        last_token_time = current_time
    return current_token

def verify_token(token):
    return token == get_current_token()

def require_auth(f):
    def decorated_function(*args, **kwargs):
        token = request.headers.get('X-API-Token')
        if not token or not verify_token(token):
            return jsonify({'error': 'Invalid or missing token'}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

ALLOWED_EXTENSIONS = {'.html', '.css', '.js', '.ico', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2', '.ttf'}

@app.route('/')
def index():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip:
        ip = ip.split(',')[0].strip()
    track_visitor(ip)
    return send_from_directory(STATIC_DIR, 'index.html')

@app.route('/vip/login')
def vip_login():
    return send_from_directory(STATIC_DIR, 'login.html')

@app.route('/vip/dashboard')
def vip_dashboard():
    return send_from_directory(STATIC_DIR, 'vip.html')

@app.route('/admin/dev')
def admin_panel():
    return send_from_directory(STATIC_DIR, 'admin.html')

@app.route('/emotes_data.json')
def serve_emotes_data():
    emotes_file = os.path.join(BASE_DIR, 'emotes_data.json')
    if os.path.exists(emotes_file):
        return send_file(emotes_file, mimetype='application/json')
    return jsonify({'error': 'Emotes data not found'}), 404

@app.route('/<path:filename>')
def serve_static(filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({'error': 'Not found'}), 404
    if '..' in filename or filename.startswith('/'):
        return jsonify({'error': 'Not found'}), 404
    return send_from_directory(STATIC_DIR, filename)

@app.route('/api/token', methods=['GET'])
def get_token_endpoint():
    return jsonify({
        'token': get_current_token(),
        'expires_in': TOKEN_ROTATION_TIME,
        'timestamp': time.time()
    })

@app.route('/api/stats', methods=['GET'])
def get_stats_endpoint():
    stats = load_stats()
    return jsonify({
        'success': True,
        'website_visits': stats.get('website_visits', 0),
        'unique_visitors': len(stats.get('unique_visitors', [])),
        'telegram_users': len(stats.get('telegram_bot_users', [])),
        'telegram_commands': stats.get('telegram_commands_count', 0),
        'dance_commands': stats.get('dance_commands', 0),
        'last_updated': stats.get('last_updated', '')
    })

@app.route('/api/info', methods=['GET'])
@require_auth
def info_endpoint():
    """Direct player info using integrated lib2 (no external API)"""
    try:
        player_id = request.args.get('player_id')
        if not player_id or not player_id.isdigit():
            return jsonify({'error': 'Missing or invalid player_id'}), 400
        
        try:
            import lib2
            return_data = asyncio.run(lib2.GetAccountInformation(player_id, "7", "ME", "/GetPlayerPersonalShow"))
            
            if return_data and not return_data.get("error"):
                basic_info = return_data.get('basicInfo', {})
                profile_info = return_data.get('profileInfo', {})
                
                return jsonify({
                    'status': 'success',
                    'player_id': player_id,
                    'nickname': basic_info.get('nickname', 'Unknown'),
                    'level': basic_info.get('level', 0),
                    'exp': basic_info.get('exp', 0),
                    'region': basic_info.get('region', 'ME'),
                    'rank': basic_info.get('rank', 'Unknown'),
                    'rankingPoints': basic_info.get('rankingPoints', 0),
                    'liked': basic_info.get('liked', 0),
                    'lastLoginAt': basic_info.get('lastLoginAt', 0),
                    'avatarId': profile_info.get('avatarId', 0),
                    'raw_data': return_data
                })
            else:
                return jsonify({
                    'error': 'Player not found',
                    'message': f'Player with UID {player_id} was not found.'
                }), 404
                
        except Exception as e:
            print(f"Error in info_endpoint: {e}")
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/info=<uid>')
def get_account_info_direct(uid):
    """Direct endpoint for player info (API style)"""
    if not uid or not uid.isdigit():
        return jsonify({
            "error": "Invalid request",
            "message": "Invalid 'uid' parameter. Please provide a valid numeric UID."
        }), 400

    try:
        import lib2
        return_data = asyncio.run(lib2.GetAccountInformation(uid, "7", "ME", "/GetPlayerPersonalShow"))
        
        if return_data and not return_data.get("error"):
            formatted_json = json.dumps(return_data, indent=2, ensure_ascii=False)
            return formatted_json, 200, {'Content-Type': 'application/json; charset=utf-8'}
        
        return jsonify({
            "error": "Player not found",
            "message": f"Player with UID {uid} was not found."
        }), 404
        
    except Exception as e:
        print(f"Error in get_account_info_direct: {e}")
        traceback.print_exc()
        return jsonify({
            "error": "Connection failed",
            "message": f"Unable to connect to servers: {str(e)}"
        }), 503

@app.route('/api/ghost', methods=['GET'])
@require_auth
def ghost_endpoint():
    try:
        team_code = request.args.get('team_code')
        ghost_name = request.args.get('ghost_name')
        ghost_count = request.args.get('count', '5')
        
        if not team_code or not ghost_name:
            return jsonify({'error': 'Missing parameters'}), 400
        
        try:
            count = int(ghost_count)
            count = min(max(count, 1), 20)
        except:
            count = 5
        
        try:
            import ghost_attack
            result = ghost_attack.sync_ghost_attack(team_code, ghost_name, count)
            
            if result.get('success'):
                return jsonify({
                    'status': 'success',
                    'message': f'Ghost Attack executed with {count} ghosts!',
                    'team_code': team_code,
                    'ghost_name': ghost_name,
                    'ghost_count': count,
                    'details': result,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return jsonify({
                    'status': 'partial',
                    'message': 'Ghost attack sent with limited success',
                    'details': result,
                    'timestamp': datetime.now().isoformat()
                })
        except Exception as ghost_error:
            print(f"Ghost attack error: {ghost_error}")
            traceback.print_exc()
            return jsonify({
                'status': 'queued',
                'message': 'Ghost Attack queued for processing',
                'team_code': team_code,
                'ghost_name': ghost_name,
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dance', methods=['GET'])
@require_auth
def dance_endpoint():
    try:
        dance_number = request.args.get('dance_number')
        team_code = request.args.get('team_code')
        uids = []
        for i in range(1, 9):
            uid = request.args.get(f'uid{i}', '')
            if uid:
                uids.append(uid)
        
        if not dance_number or not team_code:
            return jsonify({'error': 'Missing parameters'}), 400
        
        try:
            import api
            command = {
                'type': 'dance_all',
                'uids': uids,
                'emote_id': dance_number,
                'team_code': team_code,
                'timestamp': time.time()
            }
            api.pending_commands.append(command)
        except:
            pass
        
        return jsonify({
            'status': 'success',
            'message': f'Dance command received for {len(uids)} players',
            'team_code': team_code,
            'dance_number': dance_number,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/join', methods=['GET'])
@require_auth
def join_endpoint():
    try:
        team_code = request.args.get('team_code')
        if not team_code:
            return jsonify({'error': 'Missing team_code'}), 400
        
        try:
            import api
            command = {
                'type': 'join_only',
                'team_code': team_code,
                'timestamp': time.time()
            }
            api.pending_commands.append(command)
        except:
            pass
        
        return jsonify({
            'status': 'success',
            'message': f'Joining squad: {team_code}',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bot_status', methods=['GET'])
def bot_status_endpoint():
    try:
        import api
        bot_status = "online" if api.online_writer else "offline"
        return jsonify({
            'status': 'running', 
            'bot_ready': bool(api.online_writer),
            'bot_status': bot_status,
            'pending_commands': len(api.pending_commands)
        })
    except:
        return jsonify({
            'status': 'running',
            'bot_ready': False,
            'bot_status': 'offline',
            'pending_commands': 0
        })

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username', '')
        password = data.get('password', '')
        
        if validate_vip_user(username, password):
            token = secrets.token_urlsafe(32)
            vip_sessions[token] = {
                'username': username,
                'created_at': time.time(),
                'expires_at': time.time() + 86400
            }
            return jsonify({
                'success': True,
                'token': token,
                'message': 'Login successful'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid username or password'
            }), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/vip/users', methods=['GET'])
def get_vip_users():
    try:
        users = load_vip_users()
        safe_users = {}
        for username, data in users.items():
            if isinstance(data, dict):
                # Check if expired
                expires_at = data.get('expires_at')
                is_expired = False
                if expires_at:
                    try:
                        expire_date = datetime.strptime(expires_at, '%Y-%m-%d %H:%M')
                        if datetime.now() > expire_date:
                            is_expired = True
                            data['active'] = False
                    except:
                        pass
                
                safe_users[username] = {
                    'created': data.get('created', 'Unknown'),
                    'activated_at': data.get('activated_at', data.get('created', 'Unknown')),
                    'expires_at': data.get('expires_at', 'Unlimited'),
                    'days': data.get('days', 'Unlimited'),
                    'active': data.get('active', True) and not is_expired
                }
            else:
                safe_users[username] = {'created': 'System', 'active': True, 'expires_at': 'Unlimited', 'days': 'Unlimited'}
        save_vip_users(users)
        return jsonify({'success': True, 'users': safe_users})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/vip/profile', methods=['GET'])
def get_vip_profile():
    try:
        token = request.headers.get('X-VIP-Token') or request.args.get('token')
        if not token or token not in vip_sessions:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        session = vip_sessions[token]
        username = session.get('username')
        
        users = load_vip_users()
        if username not in users:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        user_data = users[username]
        if not isinstance(user_data, dict):
            return jsonify({'success': False, 'message': 'Invalid user data'}), 500
        
        # Calculate remaining days
        expires_at = user_data.get('expires_at')
        remaining_days = 'Unlimited'
        is_expired = False
        
        if expires_at and expires_at != 'Unlimited':
            try:
                expire_date = datetime.strptime(expires_at, '%Y-%m-%d %H:%M')
                now = datetime.now()
                if now > expire_date:
                    remaining_days = 0
                    is_expired = True
                else:
                    delta = expire_date - now
                    remaining_days = delta.days + 1
            except:
                pass
        
        return jsonify({
            'success': True,
            'profile': {
                'username': username,
                'activated_at': user_data.get('activated_at', user_data.get('created', 'Unknown')),
                'expires_at': expires_at or 'Unlimited',
                'total_days': user_data.get('days', 'Unlimited'),
                'remaining_days': remaining_days,
                'is_expired': is_expired,
                'active': user_data.get('active', True) and not is_expired
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/vip/users', methods=['POST'])
def add_vip_user():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        days = data.get('days', 30)
        
        try:
            days = int(days)
            if days < 1:
                days = 30
        except:
            days = 30
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400
        
        users = load_vip_users()
        if username in users:
            return jsonify({'success': False, 'message': 'User already exists'}), 400
        
        from datetime import timedelta
        activated_at = datetime.now()
        expires_at = activated_at + timedelta(days=days)
        
        users[username] = {
            'password': password,
            'created': activated_at.strftime('%Y-%m-%d %H:%M'),
            'activated_at': activated_at.strftime('%Y-%m-%d %H:%M'),
            'expires_at': expires_at.strftime('%Y-%m-%d %H:%M'),
            'days': days,
            'active': True
        }
        save_vip_users(users)
        return jsonify({'success': True, 'message': f'User {username} added successfully for {days} days'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/vip/users/<username>', methods=['DELETE'])
def delete_vip_user(username):
    try:
        users = load_vip_users()
        if username not in users:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        if username == 'admin':
            return jsonify({'success': False, 'message': 'Cannot delete admin user'}), 400
        
        del users[username]
        save_vip_users(users)
        return jsonify({'success': True, 'message': f'User {username} deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def fetch_player_info_for_outfit(uid):
    """Fetch player info for outfit display"""
    try:
        import lib2
        return_data = asyncio.run(lib2.GetAccountInformation(uid, "7", "ME", "/GetPlayerPersonalShow"))
        if return_data and not return_data.get("error"):
            return return_data
    except:
        pass
    return None

def fetch_and_process_outfit_image(image_url, size=None):
    """Fetch and process outfit image"""
    try:
        response = requests.get(image_url, timeout=10)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            if size:
                image = image.resize(size)
            return image
    except:
        pass
    return None

@app.route('/api/outfit', methods=['GET'])
@require_auth
def outfit_endpoint():
    """Generate outfit image for player - Script integrated directly"""
    try:
        player_id = request.args.get('player_id')
        if not player_id or not player_id.isdigit():
            return jsonify({'error': 'Missing or invalid player_id'}), 400
        
        player_data = fetch_player_info_for_outfit(player_id)
        if player_data is None:
            return jsonify({'error': 'Failed to fetch player info'}), 500
        
        profile_info = player_data.get("profileInfo", {})
        outfit_ids = profile_info.get("EquippedOutfit", [])
        
        if not outfit_ids:
            outfit_ids = player_data.get("AccountProfileInfo", {}).get("EquippedOutfit", [])
        
        required_starts = ["211", "214", "211", "203", "204", "205", "203"]
        fallback_ids = ["211000000", "214000000", "208000000", "203000000", "204000000", "205000000", "212000000"]
        
        used_ids = set()
        outfit_images = []
        
        def fetch_outfit_image(idx, code):
            matched = None
            for oid in outfit_ids:
                str_oid = str(oid)
                if str_oid.startswith(code) and oid not in used_ids:
                    matched = oid
                    used_ids.add(oid)
                    break
            if matched is None:
                matched = fallback_ids[idx]
            image_url = f'https://iconapi.wasmer.app/{matched}'
            return fetch_and_process_outfit_image(image_url, size=(150, 150))
        
        for idx, code in enumerate(required_starts):
            outfit_images.append(outfit_executor.submit(fetch_outfit_image, idx, code))
        
        bg_url = 'https://iili.io/39iE4rF.jpg'
        background_image = fetch_and_process_outfit_image(bg_url)
        if not background_image:
            return jsonify({'error': 'Failed to fetch background image'}), 500
        
        positions = [
            {'x': 280, 'y': 20, 'height': 150, 'width': 150},
            {'x': 470, 'y': 95, 'height': 150, 'width': 150},
            {'x': 550, 'y': 280, 'height': 150, 'width': 150},
            {'x': 470, 'y': 455, 'height': 150, 'width': 150},
            {'x': 280, 'y': 535, 'height': 150, 'width': 150},
            {'x': 100, 'y': 455, 'height': 150, 'width': 150},
            {'x': 25, 'y': 280, 'height': 150, 'width': 150}
        ]
        
        for idx, future in enumerate(outfit_images):
            outfit_image = future.result()
            if outfit_image:
                pos = positions[idx]
                resized = outfit_image.resize((pos['width'], pos['height']))
                background_image.paste(resized, (pos['x'], pos['y']), resized.convert("RGBA"))
        
        output_image = BytesIO()
        background_image.save(output_image, format='PNG')
        output_image.seek(0)
        return send_file(output_image, mimetype='image/png')
        
    except Exception as e:
        print(f"Outfit error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/outfit=<uid>')
def outfit_direct(uid):
    """Direct outfit endpoint - generates outfit image for player UID"""
    try:
        if not uid or not uid.isdigit():
            return jsonify({'error': 'Invalid UID. Please provide a valid numeric UID.'}), 400
        
        print(f"[Outfit] Generating outfit for UID: {uid}")
        
        player_data = fetch_player_info_for_outfit(uid)
        if player_data is None:
            return jsonify({'error': 'Failed to fetch player info', 'uid': uid}), 500
        
        profile_info = player_data.get("profileInfo", {})
        outfit_ids = profile_info.get("EquippedOutfit", [])
        
        if not outfit_ids:
            outfit_ids = player_data.get("AccountProfileInfo", {}).get("EquippedOutfit", [])
        
        print(f"[Outfit] Found outfit IDs: {outfit_ids}")
        
        required_starts = ["211", "214", "211", "203", "204", "205", "203"]
        fallback_ids = ["211000000", "214000000", "208000000", "203000000", "204000000", "205000000", "212000000"]
        
        used_ids = set()
        outfit_images = []
        
        def fetch_outfit_image(idx, code):
            matched = None
            for oid in outfit_ids:
                str_oid = str(oid)
                if str_oid.startswith(code) and oid not in used_ids:
                    matched = oid
                    used_ids.add(oid)
                    break
            if matched is None:
                matched = fallback_ids[idx]
            image_url = f'https://iconapi.wasmer.app/{matched}'
            return fetch_and_process_outfit_image(image_url, size=(150, 150))
        
        for idx, code in enumerate(required_starts):
            outfit_images.append(outfit_executor.submit(fetch_outfit_image, idx, code))
        
        bg_url = 'https://iili.io/39iE4rF.jpg'
        background_image = fetch_and_process_outfit_image(bg_url)
        if not background_image:
            return jsonify({'error': 'Failed to fetch background image'}), 500
        
        positions = [
            {'x': 280, 'y': 20, 'height': 150, 'width': 150},
            {'x': 470, 'y': 95, 'height': 150, 'width': 150},
            {'x': 550, 'y': 280, 'height': 150, 'width': 150},
            {'x': 470, 'y': 455, 'height': 150, 'width': 150},
            {'x': 280, 'y': 535, 'height': 150, 'width': 150},
            {'x': 100, 'y': 455, 'height': 150, 'width': 150},
            {'x': 25, 'y': 280, 'height': 150, 'width': 150}
        ]
        
        for idx, future in enumerate(outfit_images):
            outfit_img = future.result()
            if outfit_img:
                pos = positions[idx]
                resized = outfit_img.resize((pos['width'], pos['height']))
                background_image.paste(resized, (pos['x'], pos['y']), resized.convert("RGBA"))
        
        output_image = BytesIO()
        background_image.save(output_image, format='PNG')
        output_image.seek(0)
        
        print(f"[Outfit] Successfully generated outfit for UID: {uid}")
        return send_file(output_image, mimetype='image/png')
        
    except Exception as e:
        print(f"[Outfit] Error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e), 'uid': uid}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'current_token': get_current_token()[:10] + '...',
        'time': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("Starting PANEL FF on port 5000...")
    print("Developed by H4RDIXX OFFICIAL AND SK7 D5M")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
