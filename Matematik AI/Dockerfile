FROM python:3.9-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive

# Adım adım kurulum (hata ayıklama için daha iyi)
RUN apt-get update && apt-get upgrade -y

RUN apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-fonts-recommended

RUN apt-get install -y --no-install-recommends \
    texlive-latex-recommended \
    texlive-lang-european

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads outputs && chmod 777 uploads outputs

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "app:app"]
