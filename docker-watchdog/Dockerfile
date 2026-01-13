FROM python:3.9-slim

# Instalacja ffmpeg i dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Instalacja bibliotek Python
RUN pip install flask requests

# Setup
WORKDIR /app
COPY app.py .

# Wystawienie portu
EXPOSE 8085

# Start
CMD ["python", "app.py"]

