from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import OperationalError
import requests
from flasgger import Swagger

app = Flask(__name__)
Swagger(app)

# Database configuration
db_config = {
    "host": "192.168.88.254",
    "database": "Ytscraper",
    "user": "admin",
    "password": "admin",
    "port": "15015"
}

#API_KEY = "z"  # Replace with your YouTube API key
API_KEY = "z"
def get_db_connection():
    return psycopg2.connect(**db_config)

@app.route('/api/videoid', methods=['POST'])
def add_video_id():
    data = request.get_json()
    video_id = data.get('nama')
    
    if not video_id:
        return jsonify({"error": "Video ID is required"}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if video already exists
        cursor.execute("SELECT 1 FROM scraping_queue WHERE video_id = %s", (video_id,))
        if cursor.fetchone():
            return jsonify({"message": "Video ID already exists in queue"}), 400
        
        # Insert new video
        cursor.execute("""
            INSERT INTO scraping_queue (video_id, priority, status)
            VALUES (%s, 0, 'pending')
        """, (video_id,))
        conn.commit()
        
        return jsonify({"message": f"Video ID {video_id} added to queue"}), 200
        
    except OperationalError as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/channelid', methods=['POST', 'DELETE'])
def manage_channel():
    data = request.get_json()
    channel_id = data.get('nama')
    
    if not channel_id:
        return jsonify({"error": "Channel ID is required"}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if request.method == 'POST':
            # Add channel
            cursor.execute("""
                INSERT INTO youtube_channels (channel_id, channel_name)
                VALUES (%s, %s)
                ON CONFLICT (channel_id) DO NOTHING
            """, (channel_id,'nan'))
            conn.commit()
            return jsonify({"message": f"Channel ID {channel_id} added"}), 200
        
        elif request.method == 'DELETE':
            # Remove channel
            cursor.execute("DELETE FROM youtube_channels WHERE channel_id = %s", (channel_id,))
            conn.commit()
            return jsonify({"message": f"Channel ID {channel_id} removed"}), 200
            
    except OperationalError as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/check', methods=['GET', 'POST'])
def check_videos():
    # For GET requests or POST with no body, just return status
    if request.method == 'GET':
        return jsonify({"message": "Send POST with {'nama': 'runcheck'} to check for new videos"}), 200
    
    # For POST requests
    data = request.get_json() or {}
    if data.get('nama') != 'runcheck':
        return jsonify({"message": "Send {'nama': 'runcheck'} to check for new videos"}), 200
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all channel IDs
        cursor.execute("SELECT channel_id FROM youtube_channels")
        channels = [row[0] for row in cursor.fetchall()]
        
        new_videos = 0
        
        for channel_id in channels:
            # Get latest video from channel
            url = 'https://www.googleapis.com/youtube/v3/search'
            params = {
                'key': API_KEY,
                'channelId': channel_id,
                'part': 'snippet',
                'order': 'date',
                'maxResults': 1,
                'type': 'video'
            }
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'items' in data and data['items']:
                video_id = data['items'][0]['id']['videoId']
                
                # Check if video already exists
                cursor.execute("SELECT 1 FROM scraping_queue WHERE video_id = %s", (video_id,))
                if not cursor.fetchone():
                    # Insert new video
                    cursor.execute("""
                        INSERT INTO scraping_queue (video_id, priority, status)
                        VALUES (%s, 0, 'pending')
                    """, (video_id,))
                    new_videos += 1
                
                # Update last checked time
                cursor.execute("""
                    UPDATE youtube_channels 
                    SET last_checked = NOW() 
                    WHERE channel_id = %s
                """, (channel_id,))
        
        conn.commit()
        return jsonify({
            "message": "Check completed",
            "channels_checked": len(channels),
            "new_videos_found": new_videos
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Error during check: {e}"}), 500
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=15013)
