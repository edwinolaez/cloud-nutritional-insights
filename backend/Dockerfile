FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies for the Flask API service.
COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy only files needed by the API.
COPY app.py /app/app.py
COPY All_Diets.csv /app/All_Diets.csv
COPY frontend /app/frontend

EXPOSE 5000

CMD ["python", "app.py"]
