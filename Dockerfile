# Gunakan image Python yang ringan
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies sistem (dibutuhkan untuk OpenCV/EasyOCR)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy file requirements dulu (biar cache efisien)
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir biar image gak bengkak
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua source code
COPY . .

# Expose port 8000
EXPOSE 8000

# Perintah menjalankan server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]