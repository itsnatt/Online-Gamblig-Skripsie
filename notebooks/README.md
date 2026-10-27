# Notebook Deteksi Promosi Judi Online

Versi baru dari proyek lama, dipecah per bagian untuk belajar ulang. Tanpa database dan dashboard.
Setiap notebook berdiri sendiri dan bisa dijalankan di Google Colab (`File -> Upload notebook`, lalu `Runtime -> Run all`).

| Notebook | Isi | Output |
|---|---|---|
| `01_scraping_eda_cleaning.ipynb` | scraping komentar YouTube (tanpa API key), EDA data mentah, cleaning langkah demi langkah, filter & dedup, prediksi opsional | `komentar_mentah.csv`, `data_siap_predict.csv`, `hasil_prediksi.csv` |
| `02_training_model.ipynb` | training NB, SVM, RF, KNN, LR + voting, evaluasi, analisis kesalahan, eksperimen cleaning non-ASCII | `models/`, `models.zip` |
| `03_eda_dataset_kaggle.ipynb` | EDA dataset Kaggle `yaemico/judionline` | - |

Urutan belajar yang disarankan: **03 -> 02 -> 01** (pahami data, latih model, lalu pakai model untuk data hasil scraping).
Bagian prediksi di notebook 01 membutuhkan `models.zip` dari notebook 02.

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

## Cleaning non-ASCII

Komentar judi sering menyamarkan nama situs dengan huruf "fancy" (huruf bold matematika), homoglif Cyrillic,
huruf yang dipisah spasi (`P L U T O 8 8`), atau simbol dekoratif. `clean_text` melakukan dua hal sekaligus:

1. menormalkan teks agar nama situsnya terbaca (`pluto88`)
2. menambahkan token penanda (`xxfancy`, `xxhomoglyph`, `xxspaced`, `xxdecor`) agar informasi bahwa komentar itu
   disamarkan tetap menjadi fitur

Eksperimen di bagian 7 notebook 02 membandingkan cara ini dengan "buang semua" dan "biarkan mentah".
