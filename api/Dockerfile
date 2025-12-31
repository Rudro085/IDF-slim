FROM python:3.10-slim

# ---------- environment ----------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ---------- system deps ----------
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ---------- workdir ----------
WORKDIR /app

# ---------- python deps ----------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- project files ----------
COPY . .

# ---------- default command ----------
# This will be overridden by docker-compose (api / worker)
CMD ["python", "api.py"]
