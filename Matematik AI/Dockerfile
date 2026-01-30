FROM python:3.9-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive

# DIKKAT: Asagidaki komut tek bir uzun satirdir. Hicbir yerini bolme.
RUN apt-get update && apt-get install -y --no-install-recommends texlive-latex-base texlive-latex-extra texlive-lang-turkish texlive-fonts-recommended && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads outputs && chmod 777 uploads outputs

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "app:app"]
