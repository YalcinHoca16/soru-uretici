FROM python:3.9-slim

# Etkilesimsiz kurulum modu (Hatalari onler)
ENV DEBIAN_FRONTEND=noninteractive

# Gerekli LaTeX paketlerini yukle
# --no-install-recommends: Gereksiz dosyalari yuklemez (Daha hafif olur)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-lang-turkish \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Klasorleri olustur ve izin ver
RUN mkdir -p uploads outputs && chmod 777 uploads outputs

# Uygulamayi baslat (Zaman asimini 120 saniye yaptik)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "app:app"]
