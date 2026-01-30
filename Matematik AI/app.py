from flask import Flask, request, jsonify, send_from_directory
import google.generativeai as genai
import os
import uuid
import subprocess
import json

app = Flask(__name__)

# --- AYARLAR ---
# API Key'i sunucu ortam değişkenlerinden almak en güvenlisidir.
# Render'da "Environment Variables" kısmına GOOGLE_API_KEY olarak ekleyeceksin.
API_KEY = os.environ.get("GOOGLE_API_KEY", "BURAYA_API_KEY_YAZABILIRSIN_AMA_ONERILMEZ")
genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-1.5-flash"
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:5000") # Sunucu adresi

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# --- LATEX ŞABLONU ---
LATEX_TEMPLATE = r"""
\documentclass[12pt,a4paper,twoside]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[turkish,shorthands=off]{babel}
\usepackage{lmodern}
\usepackage{amsmath,amsfonts,amssymb}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{microtype}
\usepackage[a4paper, top=2cm, bottom=2.5cm, inner=2.5cm, outer=1.5cm]{geometry}
\usepackage{tcolorbox}
\tcbuselibrary{skins}
\usepackage{tabularx}
\newcolumntype{Y}{>{\centering\arraybackslash}X}
\definecolor{HeaderTeal}{RGB}{0,105,105}
\newcommand{\KonuKutusu}[2]{\begin{tcolorbox}[colframe=HeaderTeal, colback=HeaderTeal, sharp corners]\centering\bfseries\color{white}\large #1 \\ \small #2\end{tcolorbox}}
\newcommand{\Siklar}[5]{\vspace{2mm}\begin{tabularx}{\linewidth}{@{}Y Y Y Y Y@{}} \textbf{A)} #1 & \textbf{B)} #2 & \textbf{C)} #3 & \textbf{D)} #4 & \textbf{E)} #5 \end{tabularx}}

\begin{document}
\KonuKutusu{VAR_KONU}{VAR_KAZANIM}
\vspace{5mm}

% --- SORULAR BURAYA ---
\begin{tcolorbox}[title={Soru 1}, colframe=green!60!black] VAR_S1_SORU \Siklar{VAR_S1_A}{VAR_S1_B}{VAR_S1_C}{VAR_S1_D}{VAR_S1_E} \end{tcolorbox} \vspace{2mm}
\begin{tcolorbox}[title={Soru 2}, colframe=green!60!black] VAR_S2_SORU \Siklar{VAR_S2_A}{VAR_S2_B}{VAR_S2_C}{VAR_S2_D}{VAR_S2_E} \end{tcolorbox} \vspace{2mm}
\begin{tcolorbox}[title={Soru 3}, colframe=green!60!black] VAR_S3_SORU \Siklar{VAR_S3_A}{VAR_S3_B}{VAR_S3_C}{VAR_S3_D}{VAR_S3_E} \end{tcolorbox} \vspace{2mm}
\begin{tcolorbox}[title={Soru 4}, colframe=green!60!black] VAR_S4_SORU \Siklar{VAR_S4_A}{VAR_S4_B}{VAR_S4_C}{VAR_S4_D}{VAR_S4_E} \end{tcolorbox} \vspace{2mm}
\begin{tcolorbox}[title={Soru 5}, colframe=orange!75!black] VAR_S5_SORU \Siklar{VAR_S5_A}{VAR_S5_B}{VAR_S5_C}{VAR_S5_D}{VAR_S5_E} \end{tcolorbox} \vspace{2mm}
\begin{tcolorbox}[title={Soru 6}, colframe=orange!75!black] VAR_S6_SORU \Siklar{VAR_S6_A}{VAR_S6_B}{VAR_S6_C}{VAR_S6_D}{VAR_S6_E} \end{tcolorbox} \vspace{2mm}
\begin{tcolorbox}[title={Soru 7: Yeni Nesil}, colframe=purple!70!black] VAR_S7_SORU \Siklar{VAR_S7_A}{VAR_S7_B}{VAR_S7_C}{VAR_S7_D}{VAR_S7_E} \end{tcolorbox}

\end{document}
"""

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    # 1. Dosya Kontrolü
    if 'image' not in request.files:
        return jsonify({"error": "Resim yüklenmedi"}), 400
    
    file = request.files['image']
    unique_id = str(uuid.uuid4())[:8] # Dosyalar karışmasın diye rastgele ID
    filename = f"{unique_id}.jpg"
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(image_path)

    try:
        # 2. Gemini'ye Gönder
        myfile = genai.upload_file(image_path)
        model = genai.GenerativeModel(MODEL_NAME)
        
        prompt = """
        Bu matematik sorusunu analiz et. Konuyu ve kazanımı belirle. Ardından 7 adet benzer soru üret.
        Matematik ifadelerini LaTeX formatında ($...$) yaz.
        SADECE JSON formatında yanıt ver:
        {
          "konu": "...", "kazanim": "...",
          "sorular": [
            {"metin": "Soru...", "A": "...", "B": "...", "C": "...", "D": "...", "E": "..."},
            ... (toplam 7 tane)
          ]
        }
        """
        
        result = model.generate_content(
            [myfile, prompt],
            generation_config={"response_mime_type": "application/json"}
        )
        data = json.loads(result.text)

        # 3. LaTeX Dosyasını Hazırla
        tex_content = LATEX_TEMPLATE
        tex_content = tex_content.replace("VAR_KONU", data.get("konu", "Matematik"))
        tex_content = tex_content.replace("VAR_KAZANIM", data.get("kazanim", "Genel"))

        sorular = data.get("sorular", [])
        for i, s in enumerate(sorular):
            idx = i + 1
            tex_content = tex_content.replace(f"VAR_S{idx}_SORU", s.get("metin", ""))
            tex_content = tex_content.replace(f"VAR_S{idx}_A", s.get("A", "")).replace(f"VAR_S{idx}_B", s.get("B", "")).replace(f"VAR_S{idx}_C", s.get("C", "")).replace(f"VAR_S{idx}_D", s.get("D", "")).replace(f"VAR_S{idx}_E", s.get("E", ""))

        tex_filename = f"{unique_id}.tex"
        tex_path = os.path.join(OUTPUT_FOLDER, tex_filename)
        
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(tex_content)

        # 4. PDF Derle (pdflatex komutu)
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-output-directory", OUTPUT_FOLDER, tex_path],
            check=True, stdout=subprocess.DEVNULL
        )

        # 5. Sonuç URL'sini Döndür
        pdf_filename = f"{unique_id}.pdf"
        pdf_url = f"{BASE_URL}/download/{pdf_filename}"
        
        return jsonify({"success": True, "pdf_url": pdf_url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)