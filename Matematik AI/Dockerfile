FROM python:3.9-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive

# LaTeX paketlerini yükle (tek satır)
RUN apt-get update && apt-get install -y --no-install-recommends texlive-latex-base texlive-latex-extra texlive-lang-turkish texlive-fonts-recommended && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Önce sadece requirements.txt'yi kopyala (cache optimizasyonu)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sonra uygulama dosyalarını kopyala
COPY . .

# Gerekli dizinleri oluştur
RUN mkdir -p uploads outputs && chmod 777 uploads outputs

# Güvenlik: root olmayan kullanıcı oluştur (opsiyonel ama önerilen)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Uygulamayı başlat
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "app:app"]
