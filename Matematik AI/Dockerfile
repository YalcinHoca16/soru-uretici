FROM python:3.9-slim

RUN apt-get update && apt-get install -y texlive-latex-base texlive-latex-extra texlive-lang-turkish && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads outputs && chmod 777 uploads outputs

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "app:app"]
