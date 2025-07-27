Konverter ePub Arab ke Gambar dengan Ringkasan AI yang Didesain
Ringkasan Proyek
Proyek ini adalah sebuah aplikasi web yang inovatif untuk mengkonversi file ePub berbahasa Arab menjadi format visual (gambar), dilengkapi dengan kemampuan untuk menghasilkan ringkasan atau terjemahan yang relevan menggunakan Large Language Model (LLM) Google Gemini. Hasil LLM ini kemudian divisualisasikan dalam bentuk gambar yang didesain secara estetis, bahkan dengan latar belakang yang digenerate oleh AI.

Tujuan utama dari proyek ini adalah meningkatkan aksesibilitas dan pemahaman konten ePub berbahasa Arab bagi pengguna non-penutur Arab, serta mendemonstrasikan integrasi kompleks antara teknologi web development modern, pemrosesan dokumen, dan kecerdasan buatan generatif.

Daftar Isi
Fitur Utama

Arsitektur Sistem

Teknologi yang Digunakan

Prasyarat

Setup Proyek Lokal

Cara Menjalankan Aplikasi

Cara Penggunaan

Log Kinerja

Tantangan dan Solusi (Trial & Error)

Pengembangan Lanjutan

Kontribusi

Lisensi

Fitur Utama
Konversi ePub ke Gambar Halaman: Mengubah setiap halaman ePub menjadi file gambar berkualitas tinggi (PNG) menggunakan Playwright, dengan opsi untuk menampilkan/menyembunyikan rendering halaman asli untuk efisiensi.

Ekstraksi Teks & Chunking: Mengekstrak teks dan aset dari ePub, serta memecah teks panjang menjadi "chunk" untuk pemrosesan LLM yang efisien.

Ringkasan & Terjemahan AI: Memanfaatkan Google Gemini API untuk meringkas atau menerjemahkan konten ePub berdasarkan prompt pengguna, dengan implementasi dasar Retrieval-Augmented Generation (RAG) menggunakan chunking.

Visualisasi Hasil AI yang Didesain: Menghasilkan gambar unik yang berisi teks hasil LLM (ringkasan/terjemahan) dengan tata letak yang rapi dan estetis menggunakan Pillow.

Latar Belakang Gambar AI Generatif (dengan Fallback): Gambar hasil AI dapat memiliki latar belakang artistik yang digenerate oleh Stable Diffusion (via Hugging Face API). Jika generasi AI gagal (misalnya karena ketersediaan API), sistem akan menggunakan gambar fallback yang sudah didesain sebelumnya, memastikan output tetap visual. Pengguna juga dapat meminta warna latar belakang spesifik langsung dari prompt.

Dukungan Multibahasa: Mampu memproses dan menghasilkan teks dalam berbagai bahasa (terutama Arab, Indonesia, Inggris) di output LLM dan rendering gambar.

Log Kinerja Interaktif: Mencatat metrik kinerja (waktu proses, ROUGE score, jumlah halaman/chunk) ke file Excel dan menampilkannya secara interaktif di antarmuka web, dengan fitur unduh dan bersihkan log.

Penanganan API Key yang Aman: Menggunakan variabel lingkungan untuk menyimpan kunci API sensitif.

Pembersihan Otomatis: File ePub yang diunggah dan folder aset sementara dihapus otomatis setelah proses selesai.

Arsitektur Sistem
Proyek ini mengadopsi arsitektur Client-Server berbasis web:

+-------------------+        +-----------------------------------+
|    Frontend       |        |             Backend (Flask)       |
| (Web Browser)     |        |             (app.py)              |
+-------------------+        +-----------------------------------+
| - Form Upload     |        | - Menerima Unggahan               |
| - Tampilan Hasil  |        | - Orkestrasi Proses (Modul)       |
| - Log Kinerja     |------->| - Melayani File Statis/Gambar     |
+-------------------+        +-----------------------------------+
                               |                   |          |
                               V                   V          V
             +--------------------+ +--------------------+ +--------------------+
             | epub_processor.py  | | llm_integrator.py  | |  image_renderer.py |
             |--------------------| |--------------------| |--------------------|
             | - Ekstraksi ePub   | | - Google Gemini API| | - Rendering ePub   |
             | - Chunking Teks    | | - Hugging Face API | |   (Playwright)     |
             +--------------------+ +--------------------+ | - Rendering LLM    |
                                                           |   (Pillow)         |
                                                           +--------------------+
                                                                        |
                                                                        V
                                                       +---------------------------------+
                                                       |   Penyimpanan Lokal             |
                                                       |   (uploads/, generated_images/) |
                                                       +---------------------------------+

Alur Kerja Sederhana:
ePub Upload -> Ekstraksi & Chunking -> Konteks LLM -> Respons LLM -> AI Gambar Latar Belakang -> Rendering Final Gambar LLM -> Tampilan Web

Teknologi yang Digunakan
Backend: Python 3.x, Flask

Ekstraksi ePub: ebooklib, BeautifulSoup4

Chunking Teks: Fungsi kustom split_text_into_chunks

Rendering Halaman ePub: Playwright (dengan Chromium)

Rendering Gambar Hasil AI: Pillow (PIL Fork), arabic-reshaper, python-bidi

Large Language Model (LLM): Google Gemini 1.5 Flash (via Google Generative AI SDK)

AI Generasi Gambar (Latar Belakang): Stable Diffusion v1.5 (via Hugging Face Inference API)

Manajemen API Keys: Variabel Lingkungan

Log Kinerja: rouge-score, openpyxl

Frontend: HTML5, CSS3, JavaScript

Manajemen Dependensi: pip

Prasyarat
Sebelum menjalankan proyek ini, pastikan Anda memiliki:

Python 3.8+ terinstal di sistem Anda.

Git terinstal di sistem Anda.

Kunci API Google Gemini: Dapatkan dari Google AI Studio.

Token Akses Hugging Face API: Dapatkan dari Hugging Face Settings > Access Tokens (pastikan role 'read' atau 'write').

Koneksi internet aktif untuk mengakses API Gemini dan Hugging Face.

File ePub Arab untuk pengujian.

Setup Proyek Lokal
Ikuti langkah-langkah di bawah ini untuk menyiapkan dan menjalankan proyek di lingkungan lokal Anda:

Kloning Repositori:

git clone https://github.com/YOUR_USERNAME/arab-epub-to-image-web.git
cd arab-epub-to-image-web

(Ganti YOUR_USERNAME dengan nama pengguna GitHub Anda.)

Buat dan Aktifkan Virtual Environment:
Ini sangat disarankan untuk mengelola dependensi proyek secara terisolasi.

Untuk Windows (Command Prompt):

python -m venv venv
venv\Scripts\activate.bat

Untuk Windows (PowerShell):

python -m venv venv
. .\venv\Scripts\Activate.ps1
# Jika Anda mengalami masalah kebijakan eksekusi:
# Buka PowerShell SEBAGAI ADMINISTRATOR dan jalankan: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
# Lalu coba lagi perintah aktivasi di terminal biasa.

Untuk macOS/Linux:

python3 -m venv venv
source venv/bin/activate

(Anda akan melihat (venv) di awal prompt terminal Anda setelah aktivasi berhasil.)

Instal Dependensi Python:

pip install -r requirements.txt

Instal Browser Playwright:
Playwright membutuhkan biner browser yang terinstal di sistem Anda.

playwright install

(Proses ini akan mengunduh browser seperti Chromium dan mungkin memakan waktu beberapa menit.)

Unduh Font Arab (Noto Sans Arabic):
Ini krusial untuk rendering teks Arab yang benar dengan Pillow.

Buat folder fonts/ di direktori utama proyek Anda:

mkdir fonts

Unduh file NotoSansArabic-Regular.ttf dari Google Fonts.

Pindahkan file .ttf tersebut ke dalam folder fonts/ yang baru Anda buat.
(Struktur: arab-epub-to-image-web/fonts/NotoSansArabic-Regular.ttf)

Siapkan Gambar Latar Belakang Fallback (Opsional tetapi Disarankan):
Ini digunakan jika generasi gambar AI gagal.

Buat folder static/images/fallback_ai_bgs/ di dalam proyek Anda:

mkdir static\images\fallback_ai_bgs  # Untuk Windows
# mkdir -p static/images/fallback_ai_bgs # Untuk macOS/Linux

Letakkan minimal 3-5 gambar (PNG/JPG) dengan desain latar belakang sederhana/abstrak yang Anda sukai di folder ini (misalnya bg1.png, bg2.jpg). Anda bisa membuatnya sendiri atau mencari dari sumber gratis online.

Atur Kunci API (Sangat Penting):
Anda perlu mengatur kunci API Google Gemini dan token Hugging Face Anda sebagai variabel lingkungan. Lakukan ini SETIAP KALI Anda membuka terminal baru untuk menjalankan aplikasi.

Untuk Windows (PowerShell):

$env:GOOGLE_API_KEY="PASTE_YOUR_GEMINI_API_KEY_HERE"
$env:HF_API_TOKEN="PASTE_YOUR_HUGGING_FACE_TOKEN_HERE"

Untuk Windows (Command Prompt):

set GOOGLE_API_KEY=PASTE_YOUR_GEMINI_API_KEY_HERE
set HF_API_TOKEN=PASTE_YOUR_HUGGING_FACE_TOKEN_HERE

Untuk macOS/Linux:

export GOOGLE_API_KEY="PASTE_YOUR_GEMINI_API_KEY_HERE"
export HF_API_TOKEN="PASTE_YOUR_HUGGING_FACE_TOKEN_HERE"

(Ganti PASTE_YOUR_GEMINI_API_KEY_HERE dan PASTE_YOUR_HUGGING_FACE_TOKEN_HERE dengan kunci API Anda yang sebenarnya.)

Cara Menjalankan Aplikasi
Setelah semua setup selesai:

Pastikan virtual environment Anda aktif (Anda melihat (venv) di prompt terminal).

Pastikan kunci API Anda sudah diatur di sesi terminal tersebut.

Jalankan aplikasi Flask dari direktori utama proyek Anda:

python app.py

Aplikasi akan berjalan di http://127.0.0.1:5000.

Cara Penggunaan
Buka browser web Anda dan akses http://127.0.0.1:5000.

Pilih File ePub: Klik "Choose File" dan pilih file ePub berbahasa Arab (atau ePub lain) dari komputer Anda.

Masukkan Prompt untuk AI (Opsional): Di kolom teks, Anda bisa memasukkan instruksi untuk LLM Gemini.

Contoh: "Ringkas buku ini dalam 5 poin utama dalam Bahasa Indonesia."

Permintaan Warna Latar Belakang Gambar AI: Anda juga dapat meminta warna latar belakang spesifik untuk gambar hasil AI langsung di prompt Anda.

Contoh: "Ringkas buku ini dalam 3 poin. background berwarna biru!"

Warna yang dikenali: merah, biru, hijau, kuning, hitam, putih, oranye, ungu, abu-abu, coklat.

Tampilkan Gambar Halaman ePub Asli (Opsional): Centang checkbox "Tampilkan Gambar Halaman ePub Asli" jika Anda ingin melihat setiap halaman ePub dirender sebagai gambar. Hilangkan centang jika Anda hanya ingin hasil AI (ini akan mempercepat proses).

Mulai Konversi: Klik tombol "Konversi & Proses AI".

Lihat Hasil:

Pesan status akan muncul di bagian atas.

Hasil Pemrosesan AI (Teks): Teks ringkasan/terjemahan dari LLM.

Hasil Pemrosesan AI (Gambar): Gambar yang didesain secara artistik berisi teks ringkasan AI, dengan latar belakang yang digenerate AI (atau fallback) dan warna yang diminta.

Konten ePub Asli (Gambar): Jika diaktifkan, gambar dari setiap halaman ePub akan muncul.

Log Kinerja: Tabel di bagian bawah akan menampilkan detail kinerja proses terbaru.

Log Kinerja
Aplikasi ini secara otomatis mencatat data kinerja setiap proses ke file uploads/performance_log.xlsx dan menampilkannya di UI.

Unduh Log Kinerja: Klik tombol "Unduh Log Kinerja (Excel)" untuk mengunduh file Excel log.

Bersihkan Log Kinerja: Klik tombol "Bersihkan Log Kinerja" untuk menghapus semua data log dari file Excel dan UI.

Tantangan dan Solusi (Trial & Error)
Pengembangan proyek ini melibatkan berbagai tantangan teknis yang diatasi melalui proses trial and error yang sistematis:

ModuleNotFoundError & Lingkungan Virtual:

Masalah: Sering terjadi karena pustaka tidak terinstal di venv atau venv tidak aktif.

Solusi: Disiplin ketat dalam manajemen venv (python -m venv venv, venv\Scripts\activate.bat / source venv/bin/activate) dan pip install -r requirements.txt.

wkhtmltoimage Gagal Merender (0 Gambar Konten):

Masalah: Program wkhtmltoimage sering gagal merender HTML ePub kompleks atau tidak dapat menemukan aset (CSS/gambar internal), menyebabkan "0 gambar konten" dan debug log yang minim.

Solusi: Migrasi ke Playwright. Playwright, sebagai headless browser sungguhan, terbukti jauh lebih robust dalam merender HTML/CSS modern dan aset, serta menyediakan log error yang lebih baik. Implementasi dilakukan dengan menulis HTML ke file sementara di folder aset ekstrak dan menggunakan page.goto() untuk meloadnya.

Gambar Hasil LLM (Pillow) Berantakan (Teks Tumpang Tindih):

Masalah: Awalnya, teks ringkasan di gambar yang digenerate Pillow sering bertumpuk atau word-wrapping tidak rapi.

Solusi: Peningkatan signifikan pada logika wrap_text_improved di image_renderer.py. Fungsi ini sekarang lebih cerdas dalam memecah baris, menangani kata-kata panjang, dan menyesuaikan tinggi gambar secara dinamis. line_height_factor dan ukuran font disesuaikan adaptif.

Hugging Face Inference API Error 404 (AI Gambar Latar Belakang):

Masalah: Model Stable Diffusion di free inference API Hugging Face sering mengembalikan error 404 Not Found karena ketersediaan model yang tidak konsisten atau batasan rate limit.

Solusi: Implementasi Mekanisme Fallback. Jika generasi gambar AI gagal, sistem secara otomatis akan menggunakan gambar latar belakang yang sudah didesain sebelumnya dari koleksi static/images/fallback_ai_bgs/, memastikan output tetap estetis.

LLM (Gemini) Output Format HTML/Markdown Aneh:

Masalah: Gemini kadang menyertakan tag HTML (<div style="...">) atau karakter Markdown (!, **) langsung dalam respons teksnya jika diminta untuk "background".

Solusi: Prompt Engineering yang Ketat. Prompt yang dikirim ke Gemini sekarang secara eksplisit menginstruksikan model untuk "JANGAN sertakan format HTML, Markdown, atau styling apapun dalam respons Anda. Hanya berikan teks murni." Selain itu, ada pembersihan karakter format (!, **, *) di image_renderer.py sebelum teks dirender.

API Key Tidak Ditemukan (NameError):

Masalah: API Keys (GOOGLE_API_KEY, HF_API_TOKEN) tidak terbaca oleh proses Python karena masalah auto-reloader Flask atau pengaturan variabel lingkungan yang tidak konsisten.

Solusi: Pengaturan variabel lingkungan yang konsisten dan manual di terminal ($env:KEY="VALUE" atau export KEY="VALUE") setiap kali sesi baru dimulai, memastikan kunci tersedia untuk proses utama Flask dan semua modulnya.

Pengembangan Lanjutan
Proyek ini memiliki potensi pengembangan yang luas:

Fine-tuning LLM Lanjutan: Melatih model LLM (seperti Gemma atau model open-source lainnya) pada dataset ePub Arab yang lebih spesifik untuk meningkatkan akurasi ringkasan dan terjemahan dalam konteks Islami.

RAG Tingkat Lanjut: Mengimplementasikan Retrieval-Augmented Generation (RAG) yang lebih canggih dengan embeddings dan vector database (misalnya FAISS, ChromaDB) untuk pencarian konteks yang lebih semantik dan efisien dari seluruh isi buku.

Optimasi Kinerja & UX: Menambahkan progress bar yang lebih detail (misalnya dengan WebSockets) dan notifikasi real-time untuk setiap tahapan proses (ekstraksi, rendering halaman, pemanggilan AI, dll.).

Deployment Produksi: Mengembangkan aplikasi agar dapat di-deploy ke platform cloud (misalnya Google Cloud Run, AWS Elastic Beanstalk, Heroku) untuk akses publik.

Peningkatan Kustomisasi Gambar AI: Menambahkan lebih banyak opsi kustomisasi untuk gambar hasil AI (misalnya memilih gaya artistik, orientasi, resolusi) melalui antarmuka pengguna.

Kontribusi
Kontribusi pada proyek ini sangat dihargai. Silakan ajukan pull request atau buka issue jika Anda memiliki saran atau menemukan bug.

Lisensi
Proyek ini dilisensikan di bawah Lisensi MIT. Lihat file LICENSE untuk detail lebih lanjut. (Anda perlu membuat file LICENSE secara terpisah di repositori GitHub Anda jika belum ada.)
