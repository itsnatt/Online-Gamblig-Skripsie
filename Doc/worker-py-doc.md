
# YouTube Scraper & Comment Classifier - Worker Documentation

## 1. Fungsi & API Internal

### `main_loop()`

Worker utama yang berjalan terus-menerus untuk mengambil video dari antrian dan memprosesnya.

---

### `process_video(video_id)`

Memproses satu video:

1. Update status di antrian.
2. Ambil metadata video dan komentar.
3. Bersihkan & filter komentar.
4. Prediksi komentar terkait promosi judi.
5. Simpan hasil ke database.

---

### `get_next_video_from_queue()`

Mengambil `video_id` dari database `scraping_queue` dengan status `pending`, prioritas tertinggi.

---

### `update_queue_status(video_id, status)`

Mengubah status video dalam antrian (`pending`, `completed`, `failed`, `processing`).

---

### `get_video_details(api_key, video_id)`

Mengambil metadata video (judul, channel, statistik) menggunakan YouTube Data API.

---

### `get_comments_without_api(video_id)`

Mengambil komentar menggunakan `youtube-comment-downloader` (tanpa YouTube API).

---

### `clean_text(text)`

Melakukan:

* Penghapusan emoji dan bendera
* Penghapusan URL, mention, hashtag
* Lowercase dan tokenisasi
* Stopword removal

---

### `preprocess_comments(comments)`

Membersihkan komentar, menyaring berdasarkan panjang, dan menghapus duplikat.

---

### `predict_gambling_comments(comments)`

Menggunakan model klasifikasi SVM untuk menandai komentar yang terkait promosi judi.

---

### `save_to_database(video_id, video_details, comments)`

Menyimpan detail video dan komentar hasil klasifikasi ke database.

---

### `parse_comment_time(time_data)`

Mengonversi `time` komentar (baik string ISO atau float timestamp) ke objek `datetime`.

---

## 2.  Flow

1. Worker berjalan melalui fungsi `main_loop()`.
2. Ambil satu `video_id` dari antrian dengan status `pending`.
3. Ubah status ke `processing`.
4. Ambil metadata video via **YouTube API**.
5. Ambil komentar menggunakan **YoutubeCommentDownloader**.
6. Komentar dibersihkan dan disaring:

   * Emoji & simbol dihapus.
   * Tokenisasi dan stopword removal dilakukan.
   * Duplikat dan komentar terlalu pendek/panjang dibuang.
7. Komentar yang valid diproses oleh **model SVM** untuk prediksi konten judi.
8. Simpan data video & komentar ke tabel:

   * `youtube_videos`
   * `video_comments`
9. Ubah status video ke `completed` atau `failed` sesuai hasil.

---

## 3. Cara Kerja

* Proses scraping **tidak menggunakan API** untuk komentar (menghindari batasan kuota).
* **Emoji Filtering** dilakukan berdasarkan data dari `youtubeemoji.csv`.
* Model prediksi promosi judi:

  * Sudah dilatih sebelumnya (`svm_model.pkl`).
  * Memanfaatkan TF-IDF vectorizer (`tfidf_vectorizer.pkl`).
* Data disimpan secara permanen di **PostgreSQL**.

---

## 4. Stack Teknologi & Variabel

### Stack Teknologi

| Komponen                   | Deskripsi                                     |
| -------------------------- | --------------------------------------------- |
| Python                     | Bahasa pemrograman utama                      |
| psycopg2                   | Koneksi PostgreSQL                            |
| pandas                     | Pengolahan data tabular                       |
| NLTK                       | Tokenisasi dan stopword removal               |
| YouTube API Client         | Ambil metadata video                          |
| youtube-comment-downloader | Library scraping komentar YouTube (tanpa API) |
| Scikit-learn + Joblib      | Model SVM dan TF-IDF vectorizer               |

---

### ⚙️ Variabel Penting

| Variabel               | Deskripsi                                                    |
| ---------------------- | ------------------------------------------------------------ |
| `API_KEY`              | Kunci untuk mengakses YouTube Data API                       |
| `DB_CONFIG`            | Konfigurasi koneksi database PostgreSQL                      |
| `svm_model.pkl`        | Model klasifikasi promosi judi (SVM)                         |
| `tfidf_vectorizer.pkl` | Vectorizer teks berdasarkan TF-IDF                           |
| `youtubeemoji.csv`     | File berisi emoji YouTube yang sering digunakan              |
| `video_id`             | ID video YouTube yang diproses                               |
| `status`               | Status scraping video (`pending`, `processing`, `completed`) |
| `cleaned_text`         | Hasil pembersihan teks komentar                              |
| `is_gambling_promo`    | Boolean hasil prediksi komentar terkait promosi judi         |

---
