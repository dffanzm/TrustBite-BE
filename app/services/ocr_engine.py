import easyocr
import re
import cv2
import json
import os
import numpy as np
from thefuzz import process, fuzz
from app.core.config import settings
from app.models.schemas import IngredientDetail

class HalalAIEngine:
    def __init__(self):
        print("🤖 Loading AI Engine V5 (The Librarian - Read Everything)...")
        # gpu=False (CPU)
        self.reader = easyocr.Reader(['en', 'id'], gpu=False) 
        
        self.knowledge_base = self.load_database()
        # Optimize: Pre-calculate lowercase keys for speed
        self.kb_keys_lower = {k.lower(): k for k in self.knowledge_base.keys()}
        print(f"✅ Knowledge Base Loaded: {len(self.knowledge_base)} items ready to match.")

    def load_database(self):
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(base_path, "../data/ingredients.json")
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ CRITICAL: Database not found at {json_path}! {e}")
            return {}

    def preprocess_image(self, image_bytes):
        """
        V5 Image Enhancement: Fokus bikin tulisan hitam di atas putih jadi TAJAM.
        """
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # 1. Grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 2. Upscale (Penting buat tulisan kecil)
        scale_percent = 200 
        width = int(gray.shape[1] * scale_percent / 100)
        height = int(gray.shape[0] * scale_percent / 100)
        resized = cv2.resize(gray, (width, height), interpolation=cv2.INTER_CUBIC)

        # 3. Local Adaptive Thresholding (Biar bagian gelap tetep kebaca)
        # Ini lebih pinter dari simple threshold. Dia liat tetangga pixelnya.
        adaptive = cv2.adaptiveThreshold(
            resized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        # 4. Denoise (Buang bintik hitam kecil hasil threshold)
        denoised = cv2.fastNlMeansDenoising(adaptive, None, 10, 7, 21)

        is_success, buffer = cv2.imencode(".jpg", denoised)
        return buffer.tobytes()

    def is_garbage(self, text):
        """
        Detektif Sampah: Nentuin mana teks beneran, mana sampah barcode/gizi.
        """
        text = text.lower().strip()
        
        # 1. Kosong atau kependekan
        if len(text) < 3: return True
        
        # 2. Cuma angka & spasi (Barcode: "5 3 1 1")
        if re.match(r'^[\d\s]+$', text): return True
        
        # 3. Format Gizi (Angka + Satuan: "10g", "15mg", "100kcal", "0%")
        if re.match(r'^\d+(\.\d+)?\s*(g|mg|ml|kg|kcal|kj|%)$', text): return True
        
        # 4. Simbol aneh doang
        if re.match(r'^[\W_]+$', text): return True
        
        return False

    def clean_text_block(self, raw_lines):
        """
        Membersihkan list mentah dari OCR sebelum diparsing.
        """
        clean_lines = []
        
        # Area Stopwords (Kata yang menandakan ini BUKAN komposisi)
        stop_areas = ["nutrition facts", "informasi nilai gizi", "diproduksi oleh", "kode produksi", "baik digunakan sebelum"]
        
        # Area Start (Kata kunci mulai)
        start_anchors = ["ingredients", "komposisi", "bahan-bahan", "komposisi bahan"]
        
        found_start = False
        full_blob = " ".join(raw_lines).lower()
        
        # Coba cari titik potong start (biar merek gak kebaca)
        start_idx = -1
        for anchor in start_anchors:
            if anchor in full_blob:
                start_idx = full_blob.find(anchor)
                # Geser index ke setelah titik dua kalau ada "Komposisi:"
                if ":" in full_blob[start_idx:start_idx+15]:
                    start_idx = full_blob.find(":", start_idx) + 1
                else:
                    start_idx += len(anchor)
                break
        
        # Kalau ketemu 'Ingredients', potong depannya
        if start_idx != -1:
            full_blob = full_blob[start_idx:]

        # Bersihkan simbol pemisah jadi KOMA semua
        # Ganti titik(.), garis miring(/), kurung, baris baru jadi koma
        full_blob = re.sub(r'[\.\/\(\)\[\]\{\}\n]', ',', full_blob)
        
        # Hapus kata-kata Gizi/Nutrisi di tengah jalan
        for stop in stop_areas:
            full_blob = full_blob.replace(stop, " ")

        return full_blob

    def smart_parse(self, clean_blob):
        """
        Pemisah Cerdas: Memecah teks panjang jadi list bahan.
        """
        # 1. Split berdasarkan Koma
        raw_items = clean_blob.split(',')
        
        final_list = []
        
        for item in raw_items:
            # Bersihkan spasi & angka bullet point (misal "1. Gula")
            item = item.strip()
            item = re.sub(r'^\d+[\.\s]+', '', item) 
            
            # Cek Sampah Barcode/Angka
            if self.is_garbage(item):
                continue
                
            # Cek Sampah "Alien" (Kata super panjang tanpa spasi > 25 char)
            if len(item) > 25 and " " not in item:
                continue

            final_list.append(item)
            
        return final_list

    def analyze_image(self, image_bytes):
        # --- PHASE 1: OCR ---
        processed_img = self.preprocess_image(image_bytes)
        # detail=0 ambil teksnya aja
        raw_lines = self.reader.readtext(processed_img, detail=0, paragraph=False)
        
        if not raw_lines:
             return {
                "status": "UNKNOWN",
                "score": 0.0,
                "ingredients_analysis": [],
                "explanation": "Gambar gelap atau tidak ada teks. Coba nyalakan flash.",
                "raw_text": ""
            }

        # --- PHASE 2: CLEANING ---
        clean_blob = self.clean_text_block(raw_lines)
        parsed_items = self.smart_parse(clean_blob)
        
        if not parsed_items:
             return {
                "status": "UNKNOWN",
                "score": 0.0,
                "ingredients_analysis": [],
                "explanation": "Teks terdeteksi tapi terlihat seperti Barcode/Tabel Gizi. Fokuskan foto ke tulisan 'Komposisi'.",
                "raw_text": " ".join(raw_lines[:5])
            }

        # --- PHASE 3: MATCHING (THE LIBRARIAN LOGIC) ---
        analyzed_data = []
        
        # Counter
        c_haram = 0
        c_warning = 0
        c_unknown = 0
        c_safe = 0

        for item in parsed_items:
            # Default State: Anggap UNKNOWN dulu (tapi itemnya kita simpen!)
            # Ini yg lu mau: "Minyak Telon" -> Status Unknown -> Tapi Muncul di UI
            current_detail = {
                "name": item.title(), # Biar rapi Huruf Besar
                "category": "Tidak Diketahui",
                "status": "UNKNOWN",
                "description": "Bahan ini terbaca tapi tidak ada di database."
            }

            # 1. Exact Match (Cek langsung di DB)
            if item.lower() in self.kb_keys_lower:
                real_key = self.kb_keys_lower[item.lower()]
                kb_data = self.knowledge_base[real_key]
                current_detail.update({
                    "name": real_key, # Pake nama resmi dr DB
                    "category": kb_data['type'],
                    "status": kb_data['status'],
                    "description": kb_data['desc']
                })
            
            # 2. Fuzzy Match (Tebak-tebakan pinter)
            else:
                # threshold 88 biar gak halu
                best_match = process.extractOne(item, self.knowledge_base.keys(), scorer=fuzz.token_sort_ratio)
                if best_match and best_match[1] >= 88:
                    matched_key = best_match[0]
                    kb_data = self.knowledge_base[matched_key]
                    current_detail.update({
                        "name": f"{item.title()} ({matched_key})", # Tunjukin teks asli + tebakan
                        "category": kb_data['type'],
                        "status": kb_data['status'],
                        "description": kb_data['desc']
                    })

            # Masukin ke list hasil
            analyzed_data.append(IngredientDetail(**current_detail))
            
            # Update Counter
            st = current_detail['status']
            if st == "HARAM": c_haram += 1
            elif st == "WARNING": c_warning += 1
            elif st == "SAFE": c_safe += 1
            else: c_unknown += 1

        # --- PHASE 4: FINAL VERDICT ---
        final_status = "HALAL"
        score = 0.0
        explanation = ""

        total_ingredients = len(analyzed_data)

        if c_haram > 0:
            final_status = "HARAM"
            score = 0.99
            explanation = f"🚨 DITEMUKAN {c_haram} BAHAN HARAM! Jangan dikonsumsi."
        elif c_warning > 0:
            final_status = "SYUBHAT"
            score = 0.70
            explanation = f"⚠️ PERINGATAN: Ada {c_warning} bahan yang meragukan (Syubhat). Cek logo halal."
        elif c_unknown > (total_ingredients * 0.5):
            # Kalau lebih dari setengahnya gak dikenali
            final_status = "UNKNOWN"
            score = 0.40
            explanation = f"❓ INFO TERBATAS: AI membaca {total_ingredients} bahan, tapi {c_unknown} di antaranya tidak ada di database."
        else:
            final_status = "HALAL"
            score = 0.95
            explanation = "✅ TAMPAK AMAN: Mayoritas bahan dikenali dan berstatus aman/umum."

        # Sorting: Haram paling atas, lalu Warning, lalu Unknown, lalu Safe
        prio_map = {"HARAM": 0, "WARNING": 1, "UNKNOWN": 2, "SAFE": 3}
        analyzed_data.sort(key=lambda x: prio_map.get(x.status, 4))

        return {
            "status": final_status,
            "score": score,
            "ingredients_analysis": analyzed_data,
            "explanation": explanation,
            "raw_text": " ".join(raw_lines)
        }

ai_engine = HalalAIEngine()