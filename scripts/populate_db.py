import requests
import json
import os

# URL Dataset Kategori Bahan (OpenFoodFacts)
OFF_TAXONOMY_URL = "https://static.openfoodfacts.org/data/taxonomies/ingredients.json"

def generate_massive_db():
    print("🌍 Downloading World Ingredients Data...")
    try:
        response = requests.get(OFF_TAXONOMY_URL)
        data = response.json()
    except Exception as e:
        print(f"Error download: {e}")
        return

    final_db = {}
    
    # 1. LOAD DATABASE MANUAL KITA DULU (Yg tadi lu copas)
    # Supaya rule 'Babi' = HARAM tidak tertimpa data umum
    base_path = os.path.dirname(os.path.abspath(__file__))
    existing_db_path = os.path.join(base_path, "../app/data/ingredients.json")
    
    if os.path.exists(existing_db_path):
        with open(existing_db_path, 'r') as f:
            final_db = json.load(f)

    print(f"Base DB loaded: {len(final_db)} items.")

    # 2. PROSES DATA DARI INTERNET
    # OpenFoodFacts formatnya agak ribet, kita ambil yg penting aja
    count = 0
    for key, value in data.items():
        # Key biasanya format "en:tomato", kita ambil nama inggrisnya
        if not key.startswith("en:"):
            continue
            
        name = key.replace("en:", "").replace("-", " ")
        
        # Skip kalau udah ada di DB manual kita
        if name in final_db:
            continue

        # Tentukan status DEFAULT (SAFE)
        # Nanti lu bisa filter lagi keywords tertentu
        status = "SAFE"
        desc = "Bahan makanan terdaftar."
        type_ = "Umum"

        # Auto-tagging sederhana
        if "pork" in name or "bacon" in name: 
            status = "HARAM"
            type_ = "Hewani"
        elif "alcohol" in name or "wine" in name: 
            status = "HARAM"
            type_ = "Kimia"
        elif "oil" in name:
            type_ = "Minyak"
        elif "flour" in name:
            type_ = "Tepung"
            
        final_db[name] = {
            "type": type_,
            "status": status,
            "desc": desc
        }
        count += 1

    print(f"✅ Added {count} new ingredients from OpenFoodFacts!")
    print(f"🔥 Total Database Size: {len(final_db)} items.")

    # 3. SAVE KE FILE
    with open(existing_db_path, 'w') as f:
        json.dump(final_db, f, indent=2)

if __name__ == "__main__":
    generate_massive_db()