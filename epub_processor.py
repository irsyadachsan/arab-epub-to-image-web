# epub_processor.py

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import logging
import os
import re 
import shutil 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_filename(filename):
    """Membersihkan string untuk digunakan sebagai nama file yang aman."""
    cleaned_filename = re.sub(r'[\\/:*?"<>|]', '', filename)
    return cleaned_filename.replace(' ', '_')[:100]

def split_text_into_chunks(text, max_len=2000): 
    """
    Membagi teks menjadi potongan-potongan (chunks) berdasarkan panjang maksimum.
    Mencoba memecah pada spasi terdekat untuk menghindari pemotongan kata.
    """
    chunks = []
    current_text = text
    while len(current_text) > max_len:
        split_at = current_text[:max_len].rfind(' ')
        if split_at == -1: 
            split_at = max_len
        
        chunks.append(current_text[:split_at].strip())
        current_text = current_text[split_at:].strip()
    
    if current_text: 
        chunks.append(current_text.strip())
    return chunks

def extract_epub_content(epub_filepath, temp_extract_dir):
    """
    Mengekstrak konten HTML, CSS, dan gambar dari file ePub.
    Aset disimpan ke direktori sementara. HTML tidak dimodifikasi.
    
    Args:
        epub_filepath (str): Path lengkap ke file ePub.
        temp_extract_dir (str): Direktori sementara untuk menyimpan aset yang diekstrak.

    Returns:
        tuple: (list_of_raw_html_strings, list_of_local_asset_paths)
               list_of_raw_html_strings: HTML konten mentah dari ePub.
               list_of_local_asset_paths: Path lengkap ke aset lokal yang diekstrak.
    """
    raw_html_contents = [] 
    local_asset_paths = [] 
    
    if not os.path.exists(temp_extract_dir):
        os.makedirs(temp_extract_dir, exist_ok=True)
        logging.info(f"Direktori ekstraksi sementara '{temp_extract_dir}' dibuat.")

    try:
        book = epub.read_epub(epub_filepath)
        logging.info(f"Berhasil membaca file ePub: {epub_filepath}")

        # --- Langkah 1: Ekstrak semua aset (HTML, CSS, Gambar, Font) ke direktori sementara ---
        for item in book.get_items():
            # ITEM_SKIN dihapus karena tidak selalu ada di semua versi ebooklib
            if item.get_type() in [ebooklib.ITEM_STYLE, ebooklib.ITEM_IMAGE, ebooklib.ITEM_FONT, ebooklib.ITEM_COVER, ebooklib.ITEM_DOCUMENT]: 
                asset_target_path = os.path.join(temp_extract_dir, item.get_name().replace('/', os.sep))
                
                os.makedirs(os.path.dirname(asset_target_path), exist_ok=True)
                
                try:
                    with open(asset_target_path, 'wb') as f:
                        f.write(item.get_content())
                    local_asset_paths.append(asset_target_path)
                    logging.info(f"Aset diekstrak: '{asset_target_path}' dari '{item.get_name()}'")

                    # Jika ini adalah dokumen HTML, tambahkan ke daftar raw_html_contents
                    if item.get_type() == ebooklib.ITEM_DOCUMENT:
                        raw_html_contents.append(item.get_content().decode('utf-8')) # Pastikan jadi string
                        logging.info(f"HTML Mentah diekstrak dari item: {item.get_name()}")

                except Exception as e:
                    logging.warning(f"Gagal mengekstrak aset '{item.get_name()}' ke '{asset_target_path}': {e}")
            # Pastikan dokumen HTML mentah juga diambil jika tidak termasuk dalam tipe aset di atas
            # Ini penting jika ada HTML yang tidak memiliki tipe STYLE/IMAGE/FONT/COVER
            elif item.get_type() == ebooklib.ITEM_DOCUMENT and item.get_name() not in [os.path.basename(p) for p in local_asset_paths]:
                raw_html_contents.append(item.get_content().decode('utf-8'))
                logging.info(f"HTML Mentah diekstrak dari item: {item.get_name()} (dari fallback)")
                    
        if not raw_html_contents:
            logging.warning(f"Tidak ada konten HTML yang dapat diekstrak dari ePub: {epub_filepath}")

    except FileNotFoundError:
        logging.error(f"File ePub tidak ditemukan: {epub_filepath}")
        raise FileNotFoundError(f"File ePub tidak ditemukan: {epub_filepath}")
    except Exception as e:
        logging.error(f"Error saat membaca atau menguraikan ePub '{epub_filepath}': {e}", exc_info=True)
        raise Exception(f"Gagal memproses file ePub: {e}")

    return raw_html_contents, local_asset_paths 

# Contoh penggunaan (untuk pengujian)
if __name__ == '__main__':
    test_upload_dir = 'uploads' 
    test_extract_base_dir = 'temp_epub_extracts_test' 

    all_files_in_upload_dir = os.listdir(test_upload_dir)
    epub_files = [f for f in all_files_in_upload_dir if f.endswith('.epub')]

    if not epub_files:
        print(f"Tidak ada file .epub ditemukan di direktori '{test_upload_dir}'.")
        print("Silakan letakkan file .epub di sana untuk pengujian.")
    else:
        print(f"Ditemukan {len(epub_files)} file .epub di '{test_upload_dir}'.")
        for epub_filename in epub_files:
            full_epub_path = os.path.join(test_upload_dir, epub_filename)
            
            clean_name = clean_filename(os.path.splitext(epub_filename)[0])
            current_extract_dir = os.path.join(test_extract_base_dir, clean_name + "_" + str(os.getpid()))
            
            print(f"\n--- Memproses file: {epub_filename} ---")
            print(f"Mengekstrak ke: {current_extract_dir}")
            try:
                html_data, asset_paths = extract_epub_content(full_epub_path, current_extract_dir)
                print(f"Berhasil mengekstrak {len(html_data)} bagian HTML dan {len(asset_paths)} aset.")
                
                full_text_from_epub = " ".join([BeautifulSoup(html, 'html.parser').get_text(separator=' ', strip=True) for html in html_data])
                chunks = split_text_into_chunks(full_text_from_epub, max_len=1000) 
                print(f"Teks ePub dipecah menjadi {len(chunks)} chunk.")
                if chunks:
                    print(f"Chunk pertama (100 karakter): {chunks[0][:100]}...")
                    print(f"Chunk terakhir (100 karakter): {chunks[-1][-100:]}...")
                
                if os.path.exists(current_extract_dir):
                    shutil.rmtree(current_extract_dir)
                    print(f"Direktori ekstraksi '{current_extract_dir}' dihapus setelah pengujian.")

            except Exception as e:
                print(f"Gagal memproses '{epub_filename}': {e}")
                print("Pastikan file .epub tidak rusak dan valid.")
                if os.path.exists(current_extract_dir):
                    shutil.rmtree(current_extract_dir)
