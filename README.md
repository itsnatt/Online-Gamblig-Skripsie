# Deteksi Promosi Judi Online pada Komentar YouTube

Proyek ini merupakan bagian dari penelitian skripsi yang bertujuan untuk menganalisis performa beberapa algoritma machine learning dalam mendeteksi komentar promosi judi online di platform YouTube.

Sistem ini dirancang dengan pendekatan containerized dan mencakup proses pelatihan model, API inferensi, worker terjadwal, serta dashboard monitoring berbasis Grafana.

## Deskripsi Sistem

- Scraping komentar dari YouTube berdasarkan Channel ID atau Video ID
- Klasifikasi komentar menggunakan model machine learning
- Penjadwalan scraping otomatis setiap 8 jam
- Visualisasi hasil klasifikasi dan metrik performa melalui Grafana

  <img width="1920" height="931" alt="image" src="https://github.com/user-attachments/assets/daab5592-7d2b-46b5-be69-199edbec8f77" />


## Model yang Digunakan

Pelatihan model dilakukan menggunakan file `Gambling-Trainer.ipynb`, yang mencakup preprocessing data dan evaluasi performa. Algoritma yang dibandingkan antara lain:

- Support Vector Machine (SVM)
- Naive Bayes
- K-Nearest Neighbors (KNN)
- Random Forest
- Logistic Regression

