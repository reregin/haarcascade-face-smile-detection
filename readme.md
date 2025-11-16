# 🎭 Deteksi Wajah dan Senyum Real-Time (Streamlit App)

Implementasi aplikasi web Streamlit untuk deteksi wajah dan senyum secara *real-time* menggunakan OpenCV dan metode Haar Cascades.

Proyek ini dibuat untuk pemenuhan tugas akhir kelas Sistem Multimedia (TIK3051A) oleh:
1. Ahmad Triad Julianto M
2. Natalio Michael Tumuahi
3. Regina Maria Samantha George

## ⚙️ Cara Kerja

Aplikasi ini menggunakan komponen `streamlit-webrtc` untuk mengakses kamera pengguna melalui browser. Setiap *frame* video dikirim ke server (tempat skrip Streamlit berjalan), diproses menggunakan logika OpenCV, dan dikirim kembali ke browser.

1.  **Akuisisi Video:** `streamlit-webrtc` menangani pengambilan *frame* dari webcam pengguna.
2.  **Konversi Grayscale:** Setiap *frame* dikonversi ke skala abu-abu (*grayscale*).
3.  **Deteksi Wajah:** *Classifier* `haarcascade_frontalface_default.xml` diterapkan untuk menemukan lokasi wajah.
4.  **Pembuatan ROI:** Untuk setiap wajah, dibuat *Region of Interest* (ROI).
5.  **Deteksi Senyum:** *Classifier* `haarcascade_smile.xml` diterapkan **hanya di dalam ROI wajah** untuk efisiensi.
6.  **Visualisasi:** Kotak pembatas dan label digambar pada *frame*, yang kemudian dikirim kembali ke browser pengguna.

## 📦 Daftar Dependensi

Untuk menjalankan aplikasi Streamlit ini, Anda memerlukan dependensi berikut:

* **Python** (v3.7 atau lebih baru)
* **streamlit**: Framework aplikasi web.
* **opencv-python**: Untuk pemrosesan gambar dan model Haar Cascade.
* **streamlit-webrtc**: Komponen Streamlit untuk menangani streaming video *real-time*.
* **av**: Pustaka untuk pemrosesan *frame* video (diperlukan oleh `streamlit-webrtc`).

## 🚀 Panduan Eksekusi

Berikut adalah langkah-langkah untuk menjalankan program:

1.  **Simpan File**
    Simpan kode di atas dalam file bernama `app.py`.

2.  **Instal Dependensi**
    Pastikan Anda telah menginstal Python dan Pip. Buka terminal atau command prompt Anda dan jalankan perintah berikut untuk menginstal semua pustaka yang diperlukan:

    ```bash
    pip install streamlit opencv-python streamlit-webrtc av
    ```

3.  **Jalankan Aplikasi Streamlit**
    Navigasikan ke direktori tempat Anda menyimpan `app.py` dan jalankan perintah:

    ```bash
    streamlit run app.py
    ```

4.  **Operasi**
    * Aplikasi akan terbuka secara otomatis di browser web Anda.
    * Klik tombol **'START'** pada komponen video.
    * **Izinkan** browser Anda untuk mengakses kamera.
    * Aplikasi akan menampilkan video Anda dengan kotak deteksi wajah (biru) dan senyum (hijau).