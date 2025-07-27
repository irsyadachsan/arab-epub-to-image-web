# image_renderer.py

import os
import logging
import re
import shutil 

# Import Playwright
from playwright.sync_api import sync_playwright 

# Import Pillow dan library untuk teks Arab
from PIL import Image, ImageDraw, ImageFont, ImageOps 
from arabic_reshaper import reshape
from bidi.algorithm import get_display

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_filename(filename):
    """Membersihkan string untuk digunakan sebagai nama file yang aman."""
    cleaned_filename = re.sub(r'[\\/:*?"<>|]', '', filename)
    return cleaned_filename.replace(' ', '_')[:100]

# --- FUNGSI render_html_to_images (Menggunakan Playwright) ---
def render_html_to_images(html_contents, output_dir, epub_filename_prefix="epub", base_url=None):
    """
    Merender list string HTML menjadi gambar menggunakan Playwright.
    
    Args:
        html_contents (list): List dari string HTML yang akan dirender.
        output_dir (str): Direktori tempat gambar akan disimpan.
        epub_filename_prefix (str): Prefix untuk nama file gambar yang dihasilkan.
        base_url (str): Base URL untuk Playwright agar dapat menyelesaikan path relatif aset.
                        Contoh: "file:///C:/path/to/extracted_epub_assets/"
    Returns:
        list: List dari path lengkap ke gambar-gambar yang dihasilkan.
    """
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"Direktori output '{output_dir}' dibuat.")

    generated_image_paths = []

    logging.info(f"Mulai rendering {len(html_contents)} bagian HTML ke gambar menggunakan Playwright...")

    try:
        with sync_playwright() as p:
            # Launch browser (chromium, firefox, webkit)
            # headless=True untuk tidak menampilkan jendela browser
            browser = p.chromium.launch(headless=True) 
            page = browser.new_page()

            for i, html_string in enumerate(html_contents):
                clean_prefix = clean_filename(epub_filename_prefix)
                image_filename = f"{clean_prefix}_page_{i+1}.png"
                output_image_path = os.path.join(output_dir, image_filename)

                try:
                    # Tulis HTML ke file sementara di direktori ekstraksi ePub (base_url menunjuk ke sana)
                    # Ini penting agar Playwright bisa menyelesaikan path relatif ke aset (CSS, gambar)
                    local_base_path = base_url.replace('file:///', '').replace('/', os.sep)
                    temp_html_file_name = f"temp_page_{i}_{os.urandom(4).hex()}.html"
                    temp_html_full_path = os.path.join(local_base_path, temp_html_file_name)
                    
                    with open(temp_html_full_path, 'w', encoding='utf-8') as f:
                        f.write(html_string)
                    
                    # Suruh Playwright untuk pergi ke URL file lokal ini
                    file_url_for_goto = f"file:///{temp_html_full_path.replace(os.sep, '/')}"
                    
                    logging.info(f"Loading HTML for page {i+1} from {file_url_for_goto}")
                    
                    page.goto(file_url_for_goto) 
                    
                    # Tunggu hingga halaman selesai dimuat (networkidle atau load)
                    page.wait_for_load_state('networkidle') 
                    
                    # Ambil screenshot
                    # full_page=True agar tidak terpotong jika konten lebih panjang dari viewport
                    page.screenshot(path=output_image_path, full_page=True) 
                    generated_image_paths.append(output_image_path)
                    logging.info(f"Berhasil merender halaman {i+1} ke '{image_filename}' menggunakan Playwright.")
                    
                    # Hapus file HTML sementara setelah digunakan
                    os.remove(temp_html_full_path)

                except Exception as e:
                    logging.error(f"Gagal merender halaman {i+1} dari {epub_filename_prefix} menggunakan Playwright. Error: {e}", exc_info=True)
                    logging.error(f"HTML Content (partial): {html_string[:500]}...")
                    
            browser.close()
        
    except Exception as e:
        logging.error(f"Error saat menginisialisasi atau menjalankan Playwright: {e}", exc_info=True)
        logging.error("Pastikan Playwright dan browser binaries terinstal dengan benar (pip install playwright; playwright install).")

    logging.info(f"Selesai rendering. Total gambar dihasilkan: {len(generated_image_paths)}")
    return generated_image_paths


# --- FUNGSI render_llm_text_to_designed_image (Pillow) ---
def render_llm_text_to_designed_image(llm_text, output_path, max_width=800, padding=40, initial_font_size=24, line_height_factor=1.8, font_path=None, ai_background_path=None, requested_bg_color=None): 
    """
    Merender teks LLM ke gambar yang didesain menggunakan Pillow.
    Mendukung multibahasa termasuk teks Arab.
    
    Args:
        llm_text (str): Teks hasil LLM yang akan dirender.
        output_path (str): Path lengkap untuk menyimpan gambar output.
        max_width (int): Lebar maksimum gambar output (piksel).
        padding (int): Padding di sekitar teks.
        initial_font_size (int): Ukuran font awal dalam piksel. Akan disesuaikan secara adaptif.
        line_height_factor (float): Faktor pengali untuk tinggi baris (misal 1.5 = 150%).
        font_path (str): Path ke file font TrueType (.ttf/.otf) yang mendukung bahasa Arab/multibahasa.
                         Jika None, akan mencoba font default.
        ai_background_path (str, optional): Path ke gambar latar belakang yang digenerate AI.
                                            Jika None, akan menggunakan latar belakang polos.
        requested_bg_color (tuple, optional): Warna latar belakang yang diminta dalam format RGB (tuple 3 int).
                                              Jika diberikan, akan mengesampingkan ai_background_path.
    Returns:
        str: Path ke gambar yang dihasilkan jika berhasil, None jika gagal.
    """
    
    # Definisikan warna dari palet CSS kita (sesuai yang di style.css)
    primary_color = (91, 36, 28)  
    secondary_color = (160, 82, 45) 
    text_dark = (64, 47, 45) 
    background_light = (253, 250, 246) 
    
    # --- Pemuatan Font yang Lebih Robust ---
    def load_font_robust(size):
        font_obj = None
        # Prioritas 1: Font kustom yang diberikan
        if font_path and os.path.exists(font_path):
            try:
                font_obj = ImageFont.truetype(font_path, size)
                # logging.info(f"Menggunakan font kustom: {font_path} ukuran {size}")
            except IOError:
                logging.warning(f"Font kustom tidak ditemukan atau tidak valid: {font_path}. Mencoba font fallback.")
        
        # Prioritas 2: Font fallback yang umum untuk Arab dan Latin
        if font_obj is None: 
            fallback_fonts_to_try = [
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts', 'NotoSansArabic-Regular.ttf'), 
                "C:/Windows/Fonts/arial.ttf", 
                "C:/Windows/Fonts/ariblk.ttf", 
                "C:/Windows/Fonts/times.ttf", 
                "/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 
                "/System/Library/Fonts/Supplemental/Times New Roman.ttf", 
            ]
            
            loaded_font = False
            for f_path in fallback_fonts_to_try:
                if os.path.exists(f_path):
                    try:
                        font_obj = ImageFont.truetype(f_path, size)
                        # logging.info(f"Berhasil memuat font fallback: {f_path} ukuran {size}")
                        loaded_font = True
                        break
                    except Exception as e:
                        logging.warning(f"Gagal memuat font fallback '{f_path}' ukuran {size}: {e}")
            
            if not loaded_font:
                logging.warning(f"Tidak ada font yang cocok ditemukan untuk ukuran {size}. Menggunakan font default Pillow (mungkin tidak mendukung Arab dengan baik).")
                font_obj = ImageFont.load_default()
        return font_obj

    # Proses teks Arab jika ada
    is_arabic = bool(re.search(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]', llm_text))
    if is_arabic:
        reshaped_text = reshape(llm_text)
        display_text = get_display(reshaped_text) 
    else:
        display_text = llm_text
    
    # --- FUNGSI wrap_text_improved yang Diperbaiki (Lebih Akurat & Adaptif) ---
    def wrap_text_improved(text, current_font, max_width_pixels):
        lines = []
        clean_text = text.replace('**', '').replace('*', '') 
        
        # Pecah teks berdasarkan baris baru yang ada di respons LLM
        paragraphs = clean_text.split('\n')
        
        for para in paragraphs:
            if not para.strip(): 
                lines.append("")
                continue

            words = para.split(' ')
            current_line_words = []
            for word in words:
                if not word: 
                    continue
                
                test_line_str = ' '.join(current_line_words + [word])
                bbox = current_font.getbbox(test_line_str)
                text_width = bbox[2] - bbox[0] 
                
                if text_width <= max_width_pixels:
                    current_line_words.append(word)
                else:
                    if current_line_words: 
                        lines.append(' '.join(current_line_words))
                    
                    word_width = current_font.getbbox(word)[2] - current_font.getbbox(word)[0]
                    if word_width > max_width_pixels:
                        temp_word = word
                        while temp_word:
                            split_index = len(temp_word)
                            while split_index > 0 and (current_font.getbbox(temp_word[:split_index])[2] - current_font.getbbox(temp_word[:split_index])[0]) > max_width_pixels:
                                split_index -= 1
                            
                            if split_index == 0: 
                                lines.append(temp_word) 
                                break 
                            else:
                                lines.append(temp_word[:split_index] + "-") 
                                temp_word = temp_word[split_index:]
                        current_line_words = [] 
                    else:
                        current_line_words = [word]
            
            if current_line_words: 
                lines.append(' '.join(current_line_words))
        return lines

    text_width_limit = max_width - (2 * padding)

    # --- Penyesuaian Ukuran Font Adaptif ---
    max_lines_allowed = 20 
    
    current_font_size = initial_font_size
    wrapped_lines = []
    
    for _ in range(5): 
        font = load_font_robust(current_font_size)
        if font is None: 
             font = ImageFont.load_default()
             current_font_size = 18

        wrapped_lines = wrap_text_improved(display_text, font, text_width_limit)
        
        if len(wrapped_lines) <= max_lines_allowed:
            break 
        
        current_font_size -= 2 
        if current_font_size < 12: 
            current_font_size = 12
            break

    # Hitung tinggi gambar yang akurat berdasarkan teks yang sudah di-wrap
    sample_line_bbox = font.getbbox("Tg") 
    line_height = (sample_line_bbox[3] - sample_line_bbox[1]) * line_height_factor 
    total_text_height = len(wrapped_lines) * line_height
    
    image_height = int(total_text_height + (2 * padding) + 100) 
    if image_height < 300: 
        image_height = 300

    # --- LOGIKA Muat Gambar Latar Belakang AI atau Buat Kosong ---
    image = None
    if requested_bg_color: 
        logging.info(f"Menggunakan warna latar belakang yang diminta: {requested_bg_color}")
        image = Image.new('RGB', (max_width, image_height), requested_bg_color)
    elif ai_background_path and os.path.exists(ai_background_path): 
        try:
            background_image = Image.open(ai_background_path).convert("RGB")
            bg_width, bg_height = background_image.size
            
            ratio = max_width / bg_width
            new_bg_height = int(bg_height * ratio)

            background_image = background_image.resize((max_width, new_bg_height), Image.Resampling.LANCZOS)
            
            if new_bg_height > image_height: 
                start_y = (new_bg_height - image_height) // 2
                background_image = background_image.crop((0, start_y, max_width, start_y + image_height))
            elif new_bg_height < image_height: 
                temp_canvas = Image.new('RGB', (max_width, image_height), background_light)
                temp_canvas.paste(background_image, (0, 0))
                background_image = temp_canvas

            image = Image.new('RGB', (max_width, image_height), background_light) 
            image.paste(background_image, (0, 0)) 
            
            logging.info(f"Menggunakan gambar latar belakang AI dari: {ai_background_path}")
        except Exception as e:
            logging.warning(f"Gagal memuat gambar latar belakang AI '{ai_background_path}': {e}. Membuat latar belakang polos.")
            image = Image.new('RGB', (max_width, image_height), background_light)
    else: 
        logging.warning("Tidak ada gambar latar belakang AI atau warna yang diberikan. Membuat latar belakang polos.")
        image = Image.new('RGB', (max_width, image_height), background_light)

    # --- Overlay Semi-Transparan untuk Keterbacaan Teks ---
    if not requested_bg_color: 
        overlay = Image.new('RGBA', image.size, (0, 0, 0, int(255 * 0.4))) 
        image = Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(image) 
    else:
        draw = ImageDraw.Draw(image) 


    # Gambar judul "Hasil Pemrosesan AI"
    title_font_size = current_font_size + 10 
    title_font = load_font_robust(title_font_size) 
    
    title_text = "Hasil Pemrosesan AI"
    title_bbox = draw.textbbox((0,0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (max_width - title_width) / 2
    title_fill_color = (255, 255, 255) if not requested_bg_color or sum(requested_bg_color) < (255*3/2) else text_dark 
    draw.text((title_x, padding), title_text, font=title_font, fill=title_fill_color) 

    # Gambar garis bawah judul
    line_y = padding + (title_bbox[3] - title_bbox[1]) + 10
    draw.line([(max_width / 2 - 50, line_y), (max_width / 2 + 50, line_y)], fill=title_fill_color, width=3) 

    # Gambar teks LLM
    current_y = padding + (title_bbox[3] - title_bbox[1]) + 30 
    for line in wrapped_lines:
        line_bbox = draw.textbbox((0,0), line, font=font)
        line_width = line_bbox[2] - line_bbox[0]

        if is_arabic:
            text_x = max_width - padding - line_width
        else:
            text_x = padding
        
        text_fill_color = (255, 255, 255) if not requested_bg_color or sum(requested_bg_color) < (255*3/2) else text_dark
        draw.text((text_x, current_y), line, font=font, fill=text_fill_color) 
        
        current_y += line_height

    # Tambahkan border di sekeliling gambar
    border_color_rgb = (209, 198, 184) # Warna border dari CSS
    border_size = 5 # Ukuran border
    image = ImageOps.expand(image, border=border_size, fill=border_color_rgb)


    # Simpan gambar
    try:
        image.save(output_path)
        logging.info(f"Gambar hasil LLM berhasil disimpan: {output_path}")
        return output_path
    except Exception as e:
        logging.error(f"Gagal menyimpan gambar hasil LLM ke '{output_path}': {e}", exc_info=True)
        return None

# Contoh penggunaan (untuk pengujian)
if __name__ == '__main__':
    print("--- Menguji render_html_to_images (Playwright) ---")
    test_extract_dir_playwright = 'temp_playwright_test_extract'
    if os.path.exists(test_extract_dir_playwright):
        shutil.rmtree(test_extract_dir_playwright)
    os.makedirs(test_extract_dir_playwright)

    with open(os.path.join(test_extract_dir_playwright, 'style.css'), 'w') as f:
        f.write("body { font-family: sans-serif; color: blue; } h1 { color: red; }")
    Image.new('RGB', (100, 100), (255, 0, 0)).save(os.path.join(test_extract_dir_playwright, 'red_square.png'))

    sample_html_content_list_playwright = [
        f"""<html><head><link rel="stylesheet" href="style.css"></head><body><h1>Halaman Uji Playwright 1</h1><p>Ini adalah teks uji coba Playwright.</p><img src="red_square.png"></body></html>""",
        f"""<html><body><h2>Halaman Uji Playwright 2 - Arab</h2><p style='direction:rtl; text-align:right; font-family:"Arial Unicode MS", sans-serif; font-size:20px;'>مرحبا بكم في عالم الصور الرقمية!</p><p>Pengujian rendering teks Arab Playwright.</p></body></html>"""
    ]
    output_folder_playwright = 'generated_images_playwright'
    if os.path.exists(output_folder_playwright):
        shutil.rmtree(output_folder_playwright)
    os.makedirs(output_folder_playwright)

    rendered_playwright_paths = render_html_to_images(
        sample_html_content_list_playwright, 
        output_folder_playwright, 
        "test_playwright", 
        base_url=f"file:///{os.path.abspath(test_extract_dir_playwright).replace(os.sep, '/')}/"
    )
    
    if rendered_playwright_paths:
        print(f"Gambar Playwright berhasil dihasilkan: {rendered_playwright_paths}")
        print(f"Silakan cek folder '{output_folder_playwright}'")
    else:
        print("Tidak ada gambar Playwright yang dihasilkan. Cek log untuk error.")
    
    shutil.rmtree(test_extract_dir_playwright)


    print("\n--- Menguji render_llm_text_to_designed_image (Pillow) ---")
    output_folder_llm = 'generated_images_llm'
    if not os.path.exists(output_folder_llm):
        os.makedirs(output_folder_llm)
    
    for f in os.listdir(output_folder_llm):
        if 'llm_designed' in f:
            os.remove(os.path.join(output_folder_llm, f))

    test_llm_text_id = """Berikut 5 poin utama dari teks tersebut:
    
    1.  Teks membahas konsep dasar dan tujuan buku, menekankan pentingnya ilmu dan akhlak.
    2.  Menjelaskan struktur awal pembahasan yang meliputi bab-bab penting dan urutannya.
    3.  Menyajikan argumentasi tentang relevansi materi dengan kehidupan sehari-hari dan spiritualitas.
    4.  Memberikan contoh-contoh praktis atau kutipan singkat untuk mendukung argumen.
    5.  Mengakhiri dengan ajakan untuk merenungkan dan mengamalkan isi buku.
    """
    
    test_llm_text_ar = """
    هنا 3 نقاط رئيسية من النص:

    1.  النص يتحدث عن أهمية العلم والأخلاق في بناء المجتمع الإسلامي.
    2.  يشرح الكاتب منهجية الدراسة وكيفية تناول الموضوعات المعقدة ببساطة.
    3.  يؤكد على دور الفرد في تطبيق المبادئ الإسلامية في حياته اليومية.
    """
    
    custom_font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts', 'NotoSansArabic-Regular.ttf')

    dummy_ai_bg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images', 'default_llm_bg.png')
    if not os.path.exists(dummy_ai_bg_path):
        Image.new('RGB', (800, 400), (200, 200, 200)).save(dummy_ai_bg_path) 

    print("\n--- Merender Teks Bahasa Indonesia dengan Latar Belakang AI ---")
    output_id_ai_bg = os.path.join(output_folder_llm, "llm_designed_id_ai_bg.png")
    rendered_id_ai_bg_path = render_llm_text_to_designed_image(test_llm_text_id, output_id_ai_bg, 
                                                                font_path=custom_font_path, 
                                                                ai_background_path=dummy_ai_bg_path,
                                                                requested_bg_color=(255, 0, 0)) # Contoh warna merah
    if rendered_id_ai_bg_path:
        print(f"Gambar ID dengan AI BG berhasil: {rendered_id_ai_bg_path}")

    print("\n--- Merender Teks Bahasa Arab dengan Latar Belakang AI ---")
    output_ar_ai_bg = os.path.join(output_folder_llm, "llm_designed_ar_ai_bg.png")
    rendered_ar_ai_bg_path = render_llm_text_to_designed_image(test_llm_text_ar, output_ar_ai_bg, 
                                                                font_path=custom_font_path, 
                                                                ai_background_path=dummy_ai_bg_path,
                                                                requested_bg_color=(0, 0, 255)) # Contoh warna biru
    if rendered_ar_ai_bg_path:
        print(f"Gambar Arab dengan AI BG berhasil: {rendered_ar_ai_bg_path}")

    print(f"\nSilakan cek folder '{output_folder_llm}' untuk gambar yang didesain.")
