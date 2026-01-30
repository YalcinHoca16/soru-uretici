# Python 3.9 tabanlı bir Linux kur
FROM python:3.9-slim

# LaTeX ve gerekli font paketlerini yükle (Bu kısım biraz zaman alabilir)
RUN apt-get update && apt-get install -y \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-lang-turkish \
    texlive-fonts-recommended \
    && rm -rf /var/lib/apt/lists/*

# Çalışma klasörünü ayarla
WORKDIR /app

# Gereksinimleri kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodlarını kopyala
COPY . .

# Klasör izinlerini ayarla (Hata almamak için)
RUN mkdir -p uploads outputs && chmod 777 uploads outputs

# Flask uygulamasını başlat

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
