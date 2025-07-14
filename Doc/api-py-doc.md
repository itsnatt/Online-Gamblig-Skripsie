# Dokumentasi Backend YouTube Scraper API

## 1. API

### **POST `/api/videoid`**

Menambahkan `video_id` ke dalam antrian scraping.

#### **Request Body:**

```json
{
  "nama": "VIDEO_ID"
}
```

#### **Response:**

* `200 OK`: Video ID berhasil ditambahkan.
* `400 Bad Request`: Video ID sudah ada atau tidak dikirimkan.

---

### **POST `/api/channelid`**

Menambahkan channel YouTube ke dalam daftar pemantauan.

#### **Request Body:**

```json
{
  "nama": "CHANNEL_ID"
}
```

#### **Response:**

* `200 OK`: Channel berhasil ditambahkan.
* `400 Bad Request`: Channel ID tidak dikirimkan.

---

### **DELETE `/api/channelid`**

Menghapus channel dari database.

#### **Request Body:**

```json
{
  "nama": "CHANNEL_ID"
}
```

#### **Response:**

* `200 OK`: Channel berhasil dihapus.
* `400 Bad Request`: Channel ID tidak dikirimkan.

---

### **GET `/api/check`**

Menampilkan petunjuk untuk melakukan pengecekan video.

#### **Response:**

```json
{
  "message": "Send POST with {'nama': 'runcheck'} to check for new videos"
}
```

---

### **POST `/api/check`**

Melakukan pengecekan video terbaru dari setiap channel yang terdaftar dan menambahkannya ke antrian jika belum ada.

#### **Request Body:**

```json
{
  "nama": "runcheck"
}
```

#### **Response:**

```json
{
  "message": "Check completed",
  "channels_checked": 3,
  "new_videos_found": 2
}
```

---

## 2. Flow

1. **Pengguna menambahkan `video_id` secara manual** melalui endpoint `/api/videoid`.
2. **Pengguna menambahkan `channel_id`** ke database melalui endpoint `/api/channelid`.
3. **Aplikasi menyimpan channel ke tabel `youtube_channels`** (jika belum ada).
4. **Pengguna memicu pengecekan video terbaru** dengan mengirim `{ "nama": "runcheck" }` ke endpoint `/api/check`.
5. Backend akan:

   * Mengambil semua channel dari DB.
   * Memanggil **YouTube Data API** untuk mengambil video terbaru per channel.
   * Jika video belum ada di `scraping_queue`, maka ditambahkan.
6. **Waktu terakhir dicek (`last_checked`) diupdate** di DB.
7. Semua perubahan tersimpan di PostgreSQL.

---

## 3. Cara Kerja

### Fungsi Utama:

* **`add_video_id()`**

  * Memasukkan video ke tabel `scraping_queue`.
  * Mencegah duplikasi video.

* **`manage_channel()`**

  * Tambah atau hapus channel dari `youtube_channels`.

* **`check_videos()`**

  * Mengecek channel satu per satu via **YouTube API**.
  * Video terbaru akan dicek apakah sudah ada di database.
  * Jika belum, video dimasukkan ke `scraping_queue`.

### Tabel-Tabel Database:

* **`scraping_queue`**

  * Kolom: `video_id`, `priority`, `status`
* **`youtube_channels`**

  * Kolom: `channel_id`, `channel_name`, `last_checked`

### Integrasi:

* API akan memanggil YouTube Data API v3 endpoint:

  ```
  https://www.googleapis.com/youtube/v3/search
  ```

---

## 4.Stack & Variabel

### Tech Stack:

| Komponen   | Deskripsi                                |
| ---------- | ---------------------------------------- |
| Python     | Bahasa utama backend                     |
| Flask      | Web framework untuk REST API             |
| Flasgger   | Untuk dokumentasi Swagger (OpenAPI)      |
| psycopg2   | PostgreSQL client library untuk Python   |
| PostgreSQL | Database untuk menyimpan data            |
| requests   | HTTP library untuk mengakses YouTube API |

---

### Variabel Konfigurasi:

| Nama Variabel  | Deskripsi                                         |
| -------------- | ------------------------------------------------- |
| `db_config`    | Dict untuk konfigurasi koneksi ke PostgreSQL      |
| `API_KEY`      | Kunci API untuk akses YouTube Data API            |
| `video_id`     | ID unik video YouTube                             |
| `channel_id`   | ID unik channel YouTube                           |
| `channel_name` | Sementara diset ke `'nan'` (bisa diupdate manual) |
| `priority`     | Prioritas scraping video, default `0`             |
| `status`       | Status scraping, default `'pending'`              |
| `last_checked` | Timestamp pengecekan terakhir (UTC)               |

---

