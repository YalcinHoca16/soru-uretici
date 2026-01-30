FROM python:3.9-slim

# Sadece en temel LaTeX paketlerini yükle (Daha az yer kaplar)
RUN apt-get update && apt-get install -y \
    texlive-latex-base \
    texlive-lang-turkish \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Klasörleri oluştur
RUN mkdir -p uploads outputs && chmod 777 uploads outputs

# Uygulamayı başlat
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "app:app"]
