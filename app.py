import os
import sys
import time
import json
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import webbrowser
import threading

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Use resource_path to define folders
template_folder = resource_path('templates')
app = Flask(__name__, template_folder=template_folder)
CORS(app)

SAVE_FOLDER = resource_path('saved_maps')

def open_browser():
    """在新线程中打开浏览器"""
    time.sleep(1.5)  # 等待服务器启动
    webbrowser.open('http://127.0.0.1:5000/')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/visualize', methods=['POST'])
def visualize():
    data = request.json
    # 这里可以添加数据处理逻辑，例如生成框图数据
    # 目前仅返回接收到的数据
    return jsonify(data)

@app.route('/save', methods=['POST'])
def save_map():
    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)
    
    data = request.json
    project_data = data.get('projectData', {})
    path = data.get('path', '')
    is_autosave = data.get('is_autosave', False)

    # Security check for path
    if '..' in path.split('/') or os.path.isabs(path):
        return jsonify({'success': False, 'error': 'Invalid path'}), 400

    save_dir = os.path.join(SAVE_FOLDER, path)
    if not os.path.isdir(save_dir):
        return jsonify({'success': False, 'error': 'Directory not found'}), 404

    # New unified naming logic
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    path_prefix = path.replace('/', '_') if path else ''
    
    # Base filename without prefix
    if path_prefix:
        base_filename = f"{path_prefix}_{timestamp}.json"
    else:
        base_filename = f"{timestamp}.json"
        
    # Add prefix for autosave
    filename = f"autosave_{base_filename}" if is_autosave else base_filename

    filepath = os.path.join(save_dir, filename)
    
    try:
        # --- Rolling autosave deletion logic ---
        if is_autosave:
            # 1. List all autosave files in the current directory
            all_files = os.listdir(save_dir)
            autosave_files = [f for f in all_files if f.startswith('autosave_') and f.endswith('.json')]
            
            # 2. If there are 4 or more, delete the oldest one
            if len(autosave_files) >= 4:
                # Sort by creation time (oldest first)
                autosave_files.sort(key=lambda f: os.path.getctime(os.path.join(save_dir, f)))
                oldest_file = autosave_files[0]
                os.remove(os.path.join(save_dir, oldest_file))
                
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, ensure_ascii=False, indent=4)
        return jsonify({'success': True, 'filename': filename})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/maps', methods=['GET'])
def list_maps():
    path = request.args.get('path', '')
    
    # Security check for path
    # Disallow '..' and absolute paths
    if '..' in path.split('/') or os.path.isabs(path):
        return jsonify({'success': False, 'error': 'Invalid path'}), 400
        
    current_dir = os.path.join(SAVE_FOLDER, path)

    if not os.path.isdir(current_dir):
        return jsonify({'success': False, 'error': 'Directory not found'}), 404

    items = []
    for item_name in os.listdir(current_dir):
        item_path = os.path.join(current_dir, item_name)
        if os.path.isdir(item_path):
            items.append({'name': item_name, 'type': 'folder'})
        elif item_name.endswith('.json'):
            items.append({'name': item_name, 'type': 'file'})
            
    # Sort folders first, then files
    items.sort(key=lambda x: (x['type'] != 'folder', x['name']))

    return jsonify({'path': path, 'items': items})

@app.route('/load/<path:filepath>', methods=['GET'])
def load_map(filepath):
    return send_from_directory(SAVE_FOLDER, filepath)

@app.route('/create_folder', methods=['POST'])
def create_folder():
    data = request.json
    path = data.get('path', '')
    folder_name = data.get('folder_name', '')

    # Security checks
    if not folder_name or '..' in folder_name.split('/') or os.path.isabs(folder_name):
        return jsonify({'success': False, 'error': 'Invalid folder name'}), 400
    if '..' in path.split('/') or os.path.isabs(path):
        return jsonify({'success': False, 'error': 'Invalid path'}), 400

    try:
        new_folder_path = os.path.join(SAVE_FOLDER, path, folder_name)
        os.makedirs(new_folder_path, exist_ok=True)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/save_migrated', methods=['POST'])
def save_migrated_map():
    data = request.json
    project_data = data.get('projectData', {})
    filename = data.get('filename', '')

    if not filename or '..' in filename.split('/') or os.path.isabs(filename):
        return jsonify({'success': False, 'error': 'Invalid filename'}), 400
    
    filepath = os.path.join(SAVE_FOLDER, filename)

    # Security check: ensure the final path is within the intended save folder
    if not os.path.abspath(filepath).startswith(os.path.abspath(SAVE_FOLDER)):
        return jsonify({'success': False, 'error': 'Invalid path'}), 400

    if not os.path.exists(filepath):
         return jsonify({'success': False, 'error': 'Original file not found for migration save.'}), 404

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, ensure_ascii=False, indent=4)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/delete', methods=['POST'])
def delete_map():
    data = request.json
    path = data.get('path', '')
    name = data.get('name')
    item_type = data.get('type')

    if not name:
        return jsonify({'success': False, 'error': 'No name provided'}), 400

    # Security checks
    if '..' in name.split('/') or os.path.isabs(name) or '..' in path.split('/') or os.path.isabs(path):
        return jsonify({'success': False, 'error': 'Invalid path or name'}), 400

    item_path = os.path.join(SAVE_FOLDER, path, name)

    if not os.path.exists(item_path):
        return jsonify({'success': False, 'error': 'File or folder not found'}), 404
        
    try:
        if item_type == 'folder':
            os.rmdir(item_path) # Fails if not empty
        elif item_type == 'file':
            os.remove(item_path)
        else:
            return jsonify({'success': False, 'error': 'Invalid item type'}), 400
        
        return jsonify({'success': True})
    except OSError as e:
        return jsonify({'success': False, 'error': f'Cannot delete. Is the folder empty? Error: {e}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)
    # 在新线程中启动浏览器
    threading.Thread(target=open_browser).start()
    app.run(debug=True) 