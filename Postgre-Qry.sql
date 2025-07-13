-- Tabel Antrian Scraping (SIMPLE)
CREATE TABLE scraping_queue (
    video_id TEXT PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    priority INTEGER DEFAULT 0,
    status TEXT NOT NULL CHECK (status IN ('pending', 'completed')) DEFAULT 'pending'
);

-- Tabel Video (SIMPLE)
CREATE TABLE youtube_videos (
    video_id TEXT PRIMARY KEY,
    title TEXT,
    channel_name TEXT,
    published_at TIMESTAMP WITH TIME ZONE,
    view_count INTEGER,
    like_count INTEGER,
    comment_count INTEGER,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabel Komentar (SIMPLE)
CREATE TABLE video_comments (
    comment_id TEXT PRIMARY KEY,
    video_id TEXT REFERENCES youtube_videos(video_id),
    author_name TEXT,
    cleaned_text TEXT,
    published_at TIMESTAMP WITH TIME ZONE,
    is_gambling_promo BOOLEAN
);
-- Tabel daftar channel YouTube yang ingin dimonitor
CREATE TABLE youtube_channels (
    channel_id TEXT PRIMARY KEY,
    channel_name TEXT,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_checked TIMESTAMP WITH TIME ZONE
);
