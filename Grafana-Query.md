
tabel
``` 
SELECT
  vc.author_name AS user,
  yv.channel_name,
  yv.title AS video_title,
  vc.cleaned_text AS comment,
  vc.published_at,
  vc.is_gambling_promo
FROM video_comments vc
JOIN youtube_videos yv ON vc.video_id = yv.video_id
-- WHERE vc.is_gambling_promo = false
ORDER BY vc.published_at DESC
LIMIT 3000
```

ner | wordcloud
```
WITH words AS (
  SELECT
    regexp_split_to_table(LOWER(cleaned_text), '\s+') AS word
  FROM video_comments
  WHERE
    is_gambling_promo = true
    --AND published_at >= NOW() - INTERVAL '24 HOURS'
)
SELECT
  word,
  COUNT(*) AS frequency
FROM words
WHERE LENGTH(word) BETWEEN 4 AND 20
  AND word NOT IN ('yang', 'dengan', 'untuk', 'udah', 'kalo', 'tujuh', 'emang', 'bang','ngasih','nggak','sampe','beda','rela','best','rame','lgsng','bikin','jepe','bener-bener'
  ,'sehat','game','main','orang','mulu','ortu','rumah','banget','ketagihan','salam','rezeki','menang','langsung','modal','cuan','coba','terbaik','hidup','kasih','dapet','modal','maen','auto',
  'bilang','menang','keren','seru','mantap','gacir','gampang', 'konten','jepey','terima','join','temen','semangat','lancar','kayak', 'bermain')  -- Stopwords
GROUP BY word
HAVING COUNT(*) > 150 -- Menambahkan kondisi frekuensi lebih dari 200
ORDER BY frequency DESC
LIMIT 21;
```

total | stat
```
SELECT COUNT(*) 
FROM video_comments 
WHERE is_gambling_promo = true
```

top promotor | wordcloud
```
SELECT
  author_name,
  COUNT(*) AS kemunculan
FROM
  video_comments  WHERE is_gambling_promo = true
GROUP BY
  author_name
ORDER BY
  kemunculan DESC;
```

wordcloud
```
WITH words AS (
  SELECT 
    regexp_split_to_table(LOWER(cleaned_text), '\s+') AS word
  FROM video_comments
  WHERE 
    is_gambling_promo = true
    --AND published_at >= NOW() - INTERVAL '24 HOURS'
)
SELECT 
  word,
  COUNT(*) AS frequency
FROM words
WHERE LENGTH(word) BETWEEN 4 AND 20
  AND word NOT IN ('yang', 'dengan', 'untuk', 'udah', 'kalo', 'tujuh', 'emang', 'bang','ngasih','nggak','sampe','beda','rela','best','rame','lgsng'
  ,'sehat','game','main','orang','mulu','ortu','rumah')  -- Stopwords
GROUP BY word
ORDER BY frequency DESC
LIMIT 1000;
```


Prediksi pertumbuhan | timeseries
```
WITH daily_counts AS (
  SELECT 
    DATE(published_at) AS date,
    COUNT(*) AS gambling_comments
  FROM video_comments
  WHERE is_gambling_promo = true
  GROUP BY date
)
SELECT
  date,
  gambling_comments,
  AVG(gambling_comments) OVER (ORDER BY date ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS moving_avg
FROM daily_counts
ORDER BY date
```


Pertumbuhan Judi | TimeSeries
```
SELECT DATE(published_at) as date, COUNT(*) as count 
FROM video_comments 
WHERE is_gambling_promo = true 
GROUP BY date 
ORDER BY date
```


top viewr at video | Barcard
```
SELECT title, view_count 
FROM youtube_videos 
ORDER BY view_count DESC 
LIMIT 10
```

top deteksi per video | barcard
```
SELECT yv.title, COUNT(vc.comment_id) as gambling_comments
FROM video_comments vc
JOIN youtube_videos yv ON vc.video_id = yv.video_id
WHERE vc.is_gambling_promo = true
GROUP BY yv.title
ORDER BY gambling_comments DESC
LIMIT 10
```

video by channel | stat
```
-- Total Channel Unik
SELECT COUNT(DISTINCT channel_name) AS total_channels FROM youtube_videos;
-- Total Video
SELECT COUNT(*) AS total_videos FROM youtube_videos;
```


gambling by channel | barcard
```
SELECT 
  channel_name,
  COUNT(DISTINCT yv.video_id) AS total_videos,
  COUNT(DISTINCT CASE WHEN vc.is_gambling_promo = true THEN vc.comment_id END) AS gambling_comments,
  COUNT(DISTINCT CASE WHEN vc.is_gambling_promo = true THEN vc.comment_id END) * 100.0 / 
    NULLIF(COUNT(DISTINCT vc.comment_id), 0) AS gambling_percentage
FROM youtube_videos yv
LEFT JOIN video_comments vc ON yv.video_id = vc.video_id
GROUP BY channel_name
ORDER BY gambling_comments DESC
LIMIT 10
```


tabel
```
SELECT * FROM youtube_channels
```

lastScraped | tabel
```
SELECT video_id, created_at 
FROM scraping_queue 
ORDER BY created_at DESC 
LIMIT 10
```

queque | tabel
```
SELECT * FROM scraping_queue ORDER BY created_at ASC
```

scraprate | timeseries
```
SELECT DATE(scraped_at) as date, COUNT(*) as videos_scraped
FROM youtube_videos
GROUP BY date
ORDER BY date
```
