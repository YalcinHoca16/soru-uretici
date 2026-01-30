# Slim yerine TAM surumu kullaniyoruz (Daha kararli)
FROM python:3.9

# Etkilesimsiz mod (Hata riskini azaltir)
ENV DEBIAN_FRONTEND=noninteractive

# Adim 1: Depolari guncelle (Hata verirse durmasin diye ayri yazdik)
RUN apt-get update

# Adim 2: LaTeX paketlerini yukle
# --no-install-recommends komutunu kaldirdik, tam kurulum yapsin.
RUN apt-get install -y texlive-latex-base texlive-latex-extra texlive-lang-turkish

# Gereksiz dosyalari temizle
RUN rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads outputs && chmod 777 uploads outputs

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "app:app"]
