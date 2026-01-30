from flask import Flask, request, jsonify, send_from_directory
import google.generativeai as genai
import os
import uuid
import json

app = Flask(__name__)

# --- AYARLAR ---
# Render'daki Environment Variable'dan anahtarı al
API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)
MODEL_NAME = "gemini-1.5-flash"

# Klasör Ayarları
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Sunucu Adresi (Render otomatik verir veya biz elle yazarız)
BASE_URL = os.environ.get("RENDER_EXTERNAL_URL", "http://127.0.0.1:5000")

# --- HTML ŞABLONU (A4 Kağıdı Görünümü) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Matematik Çalışma Kağıdı</title>
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: #e0e0e0; /* Arka plan gri */
            margin: 0; padding: 20px;
        }
        .page {
            background: white;
            width: 210mm; /* A4 Genişliği */
            min-height: 297mm; /* A4 Yüksekliği */
            margin: 0 auto;
            padding: 20mm;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            box-sizing: border-box;
        }
        .header { 
            text-align: center; border-bottom: 2px solid #006969; 
            padding-bottom: 10px; margin-bottom: 20px; 
        }
        .header h1 { color: #006969; margin: 0; font-size: 24px; }
        .header p { color: #666; margin: 5px 0 0 0; }
        
        .question-box {
            border: 1px solid #ddd; border-radius: 8px; 
            padding: 15px; margin-bottom: 15px; page-break-inside: avoid;
        }
        .level-badge {
            display: inline-block; padding: 3px 8px; border-radius: 4px; 
            color: white; font-size: 12px; font-weight: bold; margin-bottom: 5px;
        }
        .temel { background-color: #2e7d32; }
        .orta { background-color: #ef6c00; }
        .yeni { background-color: #c62828; }

        .options { 
            display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; 
            margin-top: 15px; padding-top: 10px; border-top: 1px dashed #eee;
        }
        .opt { font-weight: bold; font-size: 14px; }

        @media print {
            body { background: white; margin: 0; padding: 0; }
            .page { box-shadow: none; margin: 0; width: 100%; }
        }
    </style>
</head>
<body>
    <div class="page">
        <div class="header">
            <h1>VAR_KONU</h1>
            <p>Kazanım: VAR_KAZANIM</p>
        </div>
        VAR_SORULAR
    </div>
</body>
</html>
"""

@app.route('/generate-html', methods=['POST'])
def generate_html():
    if 'image' not in request.files:
        return jsonify({"error": "Resim yüklenmedi"}), 400
    
    file = request.files['image']
    unique_id = str(uuid.uuid4())[:8]
    image_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}.jpg")
    file.save(image_path)

    try:
        # 1. Gemini'ye Gönder
        myfile = genai.upload_file(image_path)
        model = genai.GenerativeModel(MODEL_NAME)
        
        prompt = """
        Bu matematik sorusunu analiz et. Konuyu ve kazanımı belirle.
        Ardından bu konudan 7 adet özgün soru üret (4 temel, 2 orta, 1 yeni nesil).
        Matematik ifadelerini LaTeX formatında ($...$) yaz.
        SADECE şu JSON formatında yanıt ver:
        {
          "konu": "...", "kazanim": "...",
          "sorular": [
            {"seviye": "Temel", "metin": "...", "A": "...", "B": "...", "C": "...", "D": "...", "E": "..."},
            {"seviye": "Orta", "metin": "...", "A": "...", "B": "...", "C": "...", "D": "...", "E": "..."},
            {"seviye": "Yeni Nesil", "metin": "...", "A": "...", "B": "...", "C": "...", "D": "...", "E": "..."}
          ]
        }
        """
        
        result = model.generate_content([myfile, prompt], generation_config={"response_mime_type": "application/json"})
        data = json.loads(result.text)

        # 2. HTML İçeriğini Doldur
        sorular_html = ""
        for i, s in enumerate(data.get("sorular", [])):
            renk = "temel"
            if "Orta" in s['seviye']: renk = "orta"
            if "Yeni" in s['seviye']: renk = "yeni"

            sorular_html += f"""
            <div class="question-box">
                <span class="level-badge {renk}">Soru {i+1}: {s['seviye']}</span>
                <div>{s['metin']}</div>
                <div class="options">
                    <div class="opt">A) {s['A']}</div>
                    <div class="opt">B) {s['B']}</div>
                    <div class="opt">C) {s['C']}</div>
                    <div class="opt">D) {s['D']}</div>
                    <div class="opt">E) {s['E']}</div>
                </div>
            </div>
            """

        final_html = HTML_TEMPLATE.replace("VAR_KONU", data.get("konu", "Matematik"))
        final_html = final_html.replace("VAR_KAZANIM", data.get("kazanim", "Genel"))
        final_html = final_html.replace("VAR_SORULAR", sorular_html)

        filename = f"{unique_id}.html"
        save_path = os.path.join(OUTPUT_FOLDER, filename)
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(final_html)

        # 3. Linki Döndür
        file_url = f"{BASE_URL}/view/{filename}"
        return jsonify({"success": True, "url": file_url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/view/<filename>')
def view_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
