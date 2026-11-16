# Dockerfile for the wisata search engine backend API.
# Build from the repository root: docker build -f backend/Dockerfile -t wisata-backend .

FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install Python dependencies.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the backend application code.
COPY backend ./backend

# Expose the Uvicorn port and serve the FastAPI application.
EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
