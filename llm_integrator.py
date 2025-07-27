# llm_integrator.py
# Modul ini bertanggung jawab untuk semua interaksi dengan model AI eksternal (Google Gemini dan Hugging Face).

import google.generativeai as genai # SDK resmi Google untuk Gemini API
import os # Untuk mengakses variabel lingkungan (API Keys)
import logging # Untuk mencatat informasi, peringatan, dan error
import requests # Untuk membuat permintaan HTTP ke Hugging Face Inference API

# Konfigurasi dasar logging untuk modul ini
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def configure_gemini():
    """
    Mengkonfigurasi Google Gemini API dengan kunci API yang diambil dari variabel lingkungan.
    
    Kunci API (GOOGLE_API_KEY) harus diatur di lingkungan sistem atau sesi terminal
    sebelum aplikasi dijalankan.
    Raises:
        ValueError: Jika variabel lingkungan GOOGLE_API_KEY tidak ditemukan.
    """
    api_key = os.getenv("GOOGLE_API_KEY") # Mengambil kunci API dari variabel lingkungan
    if not api_key:
        logging.error("Variabel lingkungan GOOGLE_API_KEY tidak ditemukan.")
        raise ValueError("GOOGLE_API_KEY tidak diatur. Harap atur variabel lingkungan Anda.")
    
    genai.configure(api_key=api_key) # Mengkonfigurasi SDK Gemini dengan kunci API
    logging.info("Google Gemini API berhasil dikonfigurasi.")

def get_gemini_response(prompt_text, model_name="gemini-1.5-flash-latest"):
    """
    Mengirim prompt teks ke model Google Gemini dan mengembalikan responsnya.
    
    Args:
        prompt_text (str): Teks prompt yang akan dikirim ke model.
        model_name (str): Nama model Gemini yang akan digunakan (default: gemini-1.5-flash-latest).
                          Model ini dioptimalkan untuk kecepatan.
                          
    Returns:
        str: Teks respons dari model Gemini. Jika terjadi error atau tidak ada respons,
             mengembalikan pesan error yang informatif.
    """
    try:
        # Memastikan Gemini API sudah dikonfigurasi. Ini dipanggil setiap kali fungsi ini digunakan.
        configure_gemini() 
        
        # Membuat instance model generatif
        model = genai.GenerativeModel(model_name)
        logging.info(f"Mengirim prompt ke model {model_name}...")
        
        # Mengirim prompt dan mendapatkan respons dari model
        response = model.generate_content(prompt_text)
        
        # Memproses respons dari model
        if response.candidates:
            # Mengambil teks dari bagian pertama kandidat respons pertama
            response_text = response.candidates[0].content.parts[0].text
            logging.info("Respons dari Gemini berhasil diterima.")
            return response_text
        else:
            logging.warning("Tidak ada kandidat respons yang ditemukan dari Gemini.")
            # Memeriksa feedback dari prompt jika tidak ada kandidat (misalnya, diblokir karena keamanan)
            if response.prompt_feedback:
                logging.warning(f"Prompt feedback: {response.prompt_feedback}")
                return f"Tidak ada respons. Feedback: {response.prompt_feedback.block_reason.name}"
            return "Tidak ada respons yang dihasilkan dari model."

    except ValueError as ve:
        # Menangani error terkait konfigurasi API (misalnya, API Key tidak valid)
        logging.error(f"Kesalahan konfigurasi API saat memanggil Gemini: {ve}")
        return f"Kesalahan konfigurasi API: {ve}"
    except Exception as e:
        # Menangani error umum lainnya saat berinteraksi dengan Gemini API
        logging.error(f"Kesalahan saat berinteraksi dengan Gemini API: {e}", exc_info=True)
        return f"Terjadi kesalahan saat memproses permintaan Anda dengan AI: {e}"

# --- FUNGSI BARU: Generasi Gambar AI ---
# Ubah default model_id di sini ke runwayml/stable-diffusion-v1-5
def generate_image_from_text(image_prompt, output_filepath, model_id="runwayml/stable-diffusion-v1-5"):
    """
    Menghasilkan gambar dari prompt teks menggunakan Hugging Face Inference API.
    
    Args:
        image_prompt (str): Deskripsi teks (prompt) untuk menghasilkan gambar.
        output_filepath (str): Path lengkap di mana gambar yang dihasilkan akan disimpan.
        model_id (str): ID model Stable Diffusion di Hugging Face (default: runwayml/stable-diffusion-v1-5).
                        Model ini akan digunakan untuk inferensi.
    
    Returns:
        str: Path lengkap ke gambar yang dihasilkan jika berhasil, None jika gagal.
    """
    # Mengambil token API Hugging Face dari variabel lingkungan
    hf_api_token = os.getenv("HF_API_TOKEN")
    if not hf_api_token:
        logging.error("Variabel lingkungan HF_API_TOKEN tidak ditemukan.")
        return None
    
    # URL API inferensi Hugging Face untuk model yang ditentukan
    API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {hf_api_token}"} # Header otentikasi

    # Payload permintaan ke API
    payload = {
        "inputs": image_prompt,
        "options": {"wait_for_model": True} # Meminta API untuk menunggu jika model sedang di-load
    }

    try:
        logging.info(f"Mengirim prompt ke Hugging Face ({model_id}): '{image_prompt[:100]}...'")
        # Mengirim permintaan POST ke API
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status() # Akan memunculkan HTTPError jika status code adalah error (4xx, 5xx)

        # Memeriksa Content-Type respons untuk memastikan itu adalah gambar
        if response.headers.get("Content-Type") == "image/jpeg" or \
           response.headers.get("Content-Type") == "image/png":
            
            # Menyimpan konten respons (gambar) ke file
            with open(output_filepath, "wb") as f:
                f.write(response.content)
            logging.info(f"Gambar AI berhasil digenerate dan disimpan: {output_filepath}")
            return output_filepath
        else:
            # Jika respons bukan gambar, catat detailnya
            logging.error(f"Respons dari Hugging Face bukan gambar. Content-Type: {response.headers.get('Content-Type')}. Response: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        # Menangani error yang terjadi selama permintaan HTTP (misalnya, koneksi, 404, 500)
        logging.error(f"Error saat memanggil Hugging Face API: {e}")
        if e.response is not None: 
            logging.error(f"Response status: {e.response.status_code}, content: {e.response.text}") 
        return None
    except Exception as e:
        # Menangani error tidak terduga lainnya
        logging.error(f"Error tidak terduga saat generasi gambar AI: {e}", exc_info=True)
        return None

# Bagian ini hanya akan dieksekusi jika script ini dijalankan secara langsung (untuk pengujian modul)
if __name__ == '__main__':
    # --- Pengujian Google Gemini API ---
    # Pastikan GOOGLE_API_KEY diatur di lingkungan Anda sebelum menjalankan ini
    try:
        configure_gemini() 
    except ValueError as e:
        print(f"ERROR: {e}")
        print("Pastikan Anda sudah mengatur variabel lingkungan GOOGLE_API_KEY.")
        exit() 

    test_prompt_gemini = "Sebutkan 3 fakta menarik tentang kucing."
    print(f"\n--- Menguji Gemini dengan prompt: '{test_prompt_gemini}' ---")
    response_gemini = get_gemini_response(test_prompt_gemini)
    print("\nRespons Gemini:")
    print(response_gemini)

    arabic_text_test = "مرحبا بكم في عالم الصور الرقمية." 
    translation_prompt_test = f"Terjemahkan teks Arab berikut ke Bahasa Indonesia: '{arabic_text_test}'"
    print(f"\n--- Menguji Gemini dengan prompt terjemahan: '{translation_prompt_test}' ---")
    translated_response_test = get_gemini_response(translation_prompt_test)
    print("\nHasil Terjemahan:")
    print(translated_response_test)
    
    # --- Pengujian Generasi Gambar AI (Hugging Face Stable Diffusion) ---
    print("\n--- Menguji Generasi Gambar AI (Hugging Face Stable Diffusion) ---")
    # Pastikan HF_API_TOKEN diatur di lingkungan Anda sebelum menjalankan ini
    
    test_image_prompt_hf = "Minimalist abstract background, simple geometric shapes, soft colors, digital art."
    output_ai_image_path_hf = "generated_images/test_ai_background.png" 

    # Bersihkan file lama jika ada
    if os.path.exists(output_ai_image_path_hf):
        os.remove(output_ai_image_path_hf)

    generated_ai_image_hf = generate_image_from_text(test_image_prompt_hf, output_ai_image_path_hf)
    if generated_ai_image_hf:
        print(f"Gambar AI berhasil digenerate dan disimpan di: {generated_ai_image_hf}")
        print(f"Silakan cek folder 'generated_images' untuk 'test_ai_background.png'")
    else:
        print("Gagal generate gambar AI. Cek log di atas untuk detail error.")
