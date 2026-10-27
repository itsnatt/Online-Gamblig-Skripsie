# Notebook Deteksi Promosi Judi Online

Versi baru dari proyek lama, dipecah per bagian untuk belajar ulang. Tanpa database dan dashboard.
Setiap notebook berdiri sendiri dan bisa dijalankan di Google Colab (`File -> Upload notebook`, lalu `Runtime -> Run all`).

| Notebook | Isi | Output |
|---|---|---|
| `01_scraping_eda_cleaning.ipynb` | scraping komentar YouTube (tanpa API key), EDA data mentah, cleaning langkah demi langkah, inventaris karakter tak dikenal, filter & dedup, prediksi opsional | `komentar_mentah.csv`, `data_siap_predict.csv`, `hasil_prediksi.csv` |
| `02_training_model.ipynb` | training NB, SVM, RF, KNN, LR + voting, evaluasi, analisis kesalahan, eksperimen cleaning non-ASCII (v1 vs v2) | `models/`, `models.zip` |
| `03_eda_dataset_kaggle.ipynb` | EDA dataset Kaggle `yaemico/judionline`, termasuk trik penyamaran & emoji per label | - |
| `04_baseline_cleaning_lama.ipynb` | **baseline**: cleaning asli `worker.py` + training asli tanpa modifikasi, replikasi angka lama, lalu evaluasi adil & uji ketahanan sebagai pembanding | - |

Urutan belajar yang disarankan: **03 -> 02 -> 01** (pahami data, latih model, lalu pakai model untuk data hasil scraping).
Bagian prediksi di notebook 01 membutuhkan `models.zip` dari notebook 02. Notebook 04 bisa dijalankan kapan saja sebagai
pembanding "sebelum perbaikan".

## Menjalankan lokal (JupyterLab)

```bash
cd Online-Gamblig-Skripsie
uv venv --python 3.12 .venv            # atau: python3.12 -m venv .venv
uv pip install --python .venv/bin/python -r notebooks/requirements.txt
.venv/bin/jupyter lab notebooks/
```

Diuji dengan Python 3.12, scikit-learn 1.9, pandas 3.0, numpy 2.5.

Model `.joblib` hanya bisa dimuat dengan versi scikit-learn yang sama dengan saat training. Jadi jika notebook 02
dijalankan di Colab, jalankan notebook 01 di Colab juga (atau latih ulang di lingkungan lokal).

## Cleaning non-ASCII (versi 2)

Komentar judi sering menyamarkan nama situs dengan karakter non-ASCII. Prinsip `clean_text`: **jangan dibuang, tapi juga
jangan dipakai mentah**. Setiap jenis karakter diterjemahkan, dan tidak ada yang dihapus diam-diam:

| Jenis karakter | Hasil |
|---|---|
| huruf gaya (bold, italic, fullwidth, circled) | huruf biasa + `xxfancy` |
| huruf-emoji (huruf dalam kotak, huruf bendera berurutan >= 3) | huruf biasa + `xxfancy` (pasangan bendera tetap bendera) |
| emoji | token `emo_<nama>`, mis. `emo_money_bag`, `emo_slot_machine` |
| karakter tak terlihat (zero-width space, dsb.) | dibuang tanpa spasi agar kata tersambung + `xxinvisible` |
| huruf Cyrillic/Yunani/Armenia/Cherokee yang mirip Latin | huruf Latin + `xxhomoglyph` |
| kemiripan visual di luar tabel Unicode (lambda/delta sebagai `a`) | huruf Latin + `xxhomoglyph` (tabel `TAMBAHAN_VISUAL`) |
| `$` menempel huruf (`$ampah`) | `s` + `xxleet` (`$100` tidak berubah) |
| small caps, huruf beraksen | huruf biasa (`xxfancy` untuk small caps) |
| angka gaya (angka dalam lingkaran hitam, dsb.) | angka biasa + `xxfancy` |
| tanda baca tipografis (kutip miring, em dash) | spasi, tanpa sinyal |
| huruf aksara lain (Arab, Jepang, ...) | token `xxscript_<aksara>`, tidak diubah jadi huruf Latin |
| simbol dekoratif | spasi + `xxdecor` |
| huruf dispasi `P L U T O 8 8` | `pluto88` + `xxspaced` |
| leetspeak `m4xw1n` | **tetap** `m4xw1n` + `xxleet` (normalisasi leet untuk NER sebaiknya di kolom terpisah) |

### Kolom hasil cleaning

`siapkan_input(teks)` menghasilkan tiga kolom yang dipakai saat training **dan** prediksi:

| Kolom | Isi | Contoh |
|---|---|---|
| `text_clean` | teks bersih yang enak dibaca, termasuk token `emo_...` / `xxscript_...` di posisi aslinya | `gas main alexis17 emo_money_bag` |
| `sinyal` | penanda trik penyamaran, **terpisah** dari teks | `xxfancy xxspaced` |
| `text_min` | cleaning minimal (non-ASCII dibiarkan), hanya untuk model gabungan kata+karakter | `gas main di 𝐚𝐥𝐞𝐱𝐢𝐬𝟏𝟕 💰` |

Model = `ColumnTransformer` (TF-IDF `text_clean` + fitur biner `sinyal`) -> classifier. Cara pakai:
`model.predict(siapkan_input(["komentar ..."]))`.

Tabel homoglif diambil dari [`confusables.txt`](https://www.unicode.org/Public/security/latest/confusables.txt) resmi
Unicode (diunduh otomatis saat notebook dijalankan, sekitar 1.270 karakter). Hanya aksara yang lazim dipakai untuk menyamar
yang dipetakan. Jika unduhan gagal, notebook memakai tabel cadangan berisi 26 karakter.

Karakter yang tetap tidak bisa dipetakan dicatat di **inventaris karakter tak dikenal** (notebook 01 dan 03). Dari daftar
itu Anda bisa menemukan trik baru dan menambahkannya ke `TAMBAHAN_VISUAL`. Contohnya, lambda dan delta yang dipakai
sebagai huruf `a` (`λlexis17`, `$∆MP∆H`) ditemukan dengan cara ini. Isi tabel itu hanya karakter yang terbukti dipakai
di data, supaya komentar normal (mis. rumus matematika) tidak ikut berubah.

## Hasil singkat

| | Metode lama (`worker.py`, notebook 04) | Cleaning v2 + kolom sinyal (notebook 02) |
|---|---|---|
| F1 voting 5 model (protokol evaluasi adil) | 0,927 | **0,974** |
| Komentar promosi ber-huruf bold yang tertangkap | 12% | 100% |
| ... ber-homoglif Cyrillic | 53% | 99% |
| ... ber-small caps | 28% | 100% |

Angka F1 ~0,97 di laporan lama terlalu optimis karena kebocoran data. Dengan protokol yang adil, metode lama berada di
F1 ~0,93. Rinciannya ada di notebook 04 (bagian A-C) dan notebook 02 (bagian 7). Model gabungan kata + karakter
(notebook 02, varian D) memberi hasil terbaik secara keseluruhan.
