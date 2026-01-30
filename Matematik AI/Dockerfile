# 1. En kararlı ve hafif Python sürümünü kullan (Debian Bullseye)
FROM python:3.9-slim-bullseye

# 2. Kurulum sırasında soru sormasın (Otomatik Evet de)
ENV DEBIAN_FRONTEND=noninteractive

# 3. Güncelleme ve Yüklemeyi TEK SEFERDE yap (Bağlantı kopmasını önler)
# --fix-missing: İndiremediği paket olursa düzeltip devam etsin
RUN apt-get update && apt-get install -y --no-install-recommends --fix-missing \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-lang-turkish \
    texlive-fonts-recommended \
    && rm -rf /var/lib/apt/lists/*

# 4. Çalışma klasörünü ayarla
WORKDIR /app

# 5. Gereksinimleri yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Tüm dosyaları kopyala
COPY . .

# 7. Klasör izinlerini ayarla
RUN mkdir -p uploads outputs && chmod 777 uploads outputs

# 8. Uygulamayı başlat
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "app:app"]
