import psycopg2
import pandas as pd
import re
import emoji
from datetime import datetime
from googleapiclient.discovery import build
from youtube_comment_downloader import YoutubeCommentDownloader
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import time


import joblib
import numpy as np

# --- Load semua model dan vectorizer ---
tfidf_vectorizer = joblib.load('Model-gambling/tfidf_vectorizer.joblib')

models = {
    "NaiveBayes": joblib.load('Model-gambling/Naive Bayes.joblib'),
    "SVM": joblib.load('Model-gambling/SVM.joblib'),
    "RandomForest": joblib.load('Model-gambling/Random Forest.joblib'),
    "KNN": joblib.load('Model-gambling/KNN.joblib'),
    "LogReg": joblib.load('Model-gambling/Logistic Regression.joblib')
}

# --- Inisialisasi ---
#nltk.download('punkt')
#nltk.download('stopwords')

# Config
#API_KEY = "z"
#API_KEY = "z"
API_KEY =  "z"
DB_CONFIG = {
        "host": "192.168.88.254",
        "database": "Ytscraper",
        "user": "admin",
        "password": "admin",
        "port": "15015"
    }

# --- Load Emoji Data ---
try:
    yt_emoji_df = pd.read_csv('youtubeemoji.csv')
    yt_emoji_list = yt_emoji_df['Emoji label'].tolist()
    yt_emoji_pattern = re.compile('|'.join(re.escape(e) for e in yt_emoji_list))
except FileNotFoundError:
    print("File youtubeemoji.csv tidak ditemukan, menggunakan pola emoji default")
    yt_emoji_pattern = re.compile(r'[^\w\s,]')

# --- Fungsi Cleaning ---
def remove_flags(text):
    flags = ['🇦','🇧','🇨','🇩','🇪','🇫','🇬','🇭','🇮','🇯','🇰','🇱','🇲','🇳','🇴','🇵','🇶','🇷','🇸','🇹','🇺','🇻','🇼','🇽','🇾','🇿']
    return ''.join(c for c in text if c not in flags)

def clean_text(text):
    if pd.isna(text): return ''
    
    text = str(text)
    text = emoji.replace_emoji(text, replace='')  # Hapus semua emoji
    text = remove_flags(text)
    text = yt_emoji_pattern.sub('', text)  # Hapus emoji khusus YouTube
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)  # Hapus URL
    text = re.sub(r'@\w+|\#\w+', '', text)  # Hapus mention dan hashtag
    text = re.sub(r'\n', ' ', text)  # Hapus newline
    text = re.sub(r'\s+', ' ', text).strip()  # Normalisasi spasi
    
    # Tokenisasi dengan stopwords Bahasa Indonesia
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('indonesian'))
    tokens = [w for w in tokens if w not in stop_words]
    
    return ' '.join(tokens)

# --- Fungsi Database ---
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def get_next_video_from_queue():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Ambil video dengan status pending dan prioritas tertinggi
    cur.execute("""
        SELECT video_id FROM scraping_queue 
        WHERE status = 'pending' 
        ORDER BY priority DESC, created_at ASC 
        LIMIT 1 FOR UPDATE SKIP LOCKED
    """)
    
    result = cur.fetchone()
    conn.close()
    
    return result[0] if result else None

def update_queue_status(video_id, status):
    # Hanya izinkan status yang sesuai constraint
    allowed_statuses = ['pending', 'completed']
    if status not in allowed_statuses:
        status = 'pending'  # Fallback ke default
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE scraping_queue 
        SET status = %s 
        WHERE video_id = %s
    """, (status, video_id))
    conn.commit()
    conn.close()
# --- Fungsi Scraping ---
def get_video_details(api_key, video_id):
    youtube = build("youtube", "v3", developerKey=api_key)
    try:
        response = youtube.videos().list(
            part="snippet,statistics",
            id=video_id
        ).execute()
        
        if response["items"]:
            item = response["items"][0]
            return {
                "title": item["snippet"]["title"],
                "channel_name": item["snippet"]["channelTitle"],
                "published_at": item["snippet"]["publishedAt"],
                "view_count": int(item["statistics"].get("viewCount", 0)),
                "like_count": int(item["statistics"].get("likeCount", 0)),
                "comment_count": int(item["statistics"].get("commentCount", 0))
            }
    except Exception as e:
        print(f"Error YouTube API: {e}")
    return None

def get_comments_without_api(video_id):
    downloader = YoutubeCommentDownloader()
    comments = []
    
    try:
        for comment in downloader.get_comments_from_url(f'https://www.youtube.com/watch?v={video_id}', sort_by=0):
            comments.append({
                "author": comment['author'].lstrip('@'),
                "published_at": comment.get('time', comment.get('time_parsed', time.time())),
                "text": comment['text'],  # Simpan sebagai 'text' bukan 'original_text'
                "is_gambling_promo": None
            })
    except Exception as e:
        print(f"Error mengambil komentar: {e}")
    
    return comments

# --- Fungsi Processing ---
def preprocess_comments(comments):
    if not comments:
        return []
    
    df = pd.DataFrame(comments)
    
    # 1. Cleaning
    df['cleaned_text'] = df['text'].apply(clean_text)
    
    # 2. Filter panjang teks
    df['text_length'] = df['cleaned_text'].str.len()
    df = df[(df['text_length'] >= 10) & (df['text_length'] <= 70)]
    
    # 3. Hapus duplikat (spam)
    df.drop_duplicates(subset=['cleaned_text'], keep='first', inplace=True)
    
    return df.to_dict('records')


def predict_gambling_comments(comments):
    if not comments:
        return comments

    texts = [comment['cleaned_text'] for comment in comments]
    texts_tfidf = tfidf_vectorizer.transform(texts)

    # Ambil prediksi dari semua model
    predictions_all = []
    for model_name, model in models.items():
        preds = model.predict(texts_tfidf)
        predictions_all.append(preds)

    # Voting: mayoritas 1 -> True, mayoritas 0 -> False
    predictions_all = np.array(predictions_all)  # shape: (5_models, N_komentar)
    votes = np.round(np.mean(predictions_all, axis=0)).astype(int)  # Hasil voting mayoritas

    for comment, pred in zip(comments, votes):
        comment['is_gambling_promo'] = bool(pred)

    return comments




def save_to_database(video_id, video_details, comments):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 1. Simpan video details (unchanged)
        cur.execute("""
            INSERT INTO youtube_videos (
                video_id, title, channel_name, published_at, 
                view_count, like_count, comment_count
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (video_id) DO UPDATE SET
                title = EXCLUDED.title,
                channel_name = EXCLUDED.channel_name,
                view_count = EXCLUDED.view_count,
                like_count = EXCLUDED.like_count,
                comment_count = EXCLUDED.comment_count
        """, (
            video_id,
            video_details['title'],
            video_details['channel_name'],
            datetime.strptime(video_details['published_at'], '%Y-%m-%dT%H:%M:%SZ'),
            video_details['view_count'],
            video_details['like_count'],
            video_details['comment_count']
        ))
        
        # 2. Simpan komentar dengan generate comment_id
        for comment in comments:
            # Generate consistent comment_id from cleaned text + timestamp
            comment_id = str(abs(hash(f"{comment['cleaned_text']}{comment['published_at']}")))[:12]
            published_at = parse_comment_time(comment['published_at'])
            cur.execute("""
                INSERT INTO video_comments (
                    comment_id, video_id, author_name, 
                    cleaned_text, published_at, is_gambling_promo
                ) VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (comment_id) DO UPDATE SET
                    cleaned_text = EXCLUDED.cleaned_text,
                    is_gambling_promo = EXCLUDED.is_gambling_promo
            """, (
                comment_id,  # Generated ID
                video_id,
                comment['author'],
                comment['cleaned_text'],
                published_at,
                comment.get('is_gambling_promo', False)  # Default False if not provided
            ))
        
        conn.commit()
        print(f"Disimpan {len(comments)} komentar untuk video {video_id}")
        
    except Exception as e:
        print(f"Database error: {e}")
        if conn: conn.rollback()
    finally:
        if conn: conn.close()


from datetime import datetime
import time

def parse_comment_time(time_data):
    """Handle both string and float timestamp formats"""
    if isinstance(time_data, float):
        # Jika berupa timestamp float (unix time)
        return datetime.fromtimestamp(time_data)
    elif isinstance(time_data, str):
        try:
            # Coba format dengan timezone (YouTube format)
            return datetime.strptime(time_data, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                # Coba format tanpa timezone
                return datetime.strptime(time_data, '%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                # Fallback ke waktu sekarang
                return datetime.now()
    else:
        return datetime.now()
# --- Main Worker ---
def process_video(video_id):
    print(f"\nMemproses video {video_id}...")
    
    try:
        # 1. Update status menjadi 'processing'
        update_queue_status(video_id, 'processing')
        
        # 2. Scraping
        video_details = get_video_details(API_KEY, video_id)
        if not video_details:
            print("Video tidak ditemukan atau error API")
            update_queue_status(video_id, 'failed')
            return
        
        comments = get_comments_without_api(video_id)
        print(f"Ditemukan {len(comments)} komentar")
        
        # 3. Preprocessing
        processed_comments = preprocess_comments(comments)
        print(f"Setelah preprocessing: {len(processed_comments)} komentar valid")
        
        # 4. Predicting
        predicted_comments = predict_gambling_comments(processed_comments)
        
        # 5. Save to DB
        save_to_database(video_id, video_details, predicted_comments)
        
        # 6. Update status menjadi 'completed'
        update_queue_status(video_id, 'completed')
        
    except Exception as e:
        print(f"Error memproses video {video_id}: {e}")
        update_queue_status(video_id, 'failed')

# --- Main Loop ---
def main_loop():
    print("Memulai worker scraping YouTube...")
    while True:
        video_id = get_next_video_from_queue()
        
        if video_id:
            process_video(video_id)
        else:
            print("Tidak ada video dalam antrian, menunggu 60 detik...")
            time.sleep(60)

if __name__ == "__main__":
    main_loop()
