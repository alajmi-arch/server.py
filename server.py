from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os

app = Flask(__name__)

# تحديد مسار الملفات التي سيتم مشاركتها
UPLOAD_FOLDER = "shared_files"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# قاعدة بيانات SQLite
DB_FILE = "server_data.db"

def init_db():
    """تهيئة قاعدة البيانات."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/upload', methods=['POST'])
def upload_file():
    """رفع ملفات إلى الخادم."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return jsonify({"message": f"File {file.filename} uploaded successfully"}), 200

@app.route('/files/<filename>', methods=['GET'])
def download_file(filename):
    """تحميل الملفات."""
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/data', methods=['GET', 'POST'])
def manage_data():
    """إضافة أو استرجاع البيانات."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        key = data.get('key')
        value = data.get('value')
        
        if not key or not value:
            return jsonify({"error": "Key and value are required"}), 400
        
        cursor.execute('''
            INSERT OR REPLACE INTO data (key, value) VALUES (?, ?)
        ''', (key, value))
        conn.commit()
        return jsonify({"message": f"Data saved: {key} -> {value}"}), 200
    
    elif request.method == 'GET':
        cursor.execute('SELECT * FROM data')
        rows = cursor.fetchall()
        data = {row[0]: row[1] for row in rows}
        return jsonify(data), 200
    
    conn.close()

if __name__ == '__main__':
    init_db()
    # تشغيل السيرفر على كل العناوين المتاحة
    app.run(host='0.0.0.0', port=5000)
