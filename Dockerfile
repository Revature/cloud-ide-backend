# Use a small, official Python image
FROM python:3.10-slim

# Set a working directory for your app code
WORKDIR /app

# Copy in only requirements first (to improve Docker layer caching)
COPY requirements.txt .

# Install dependencies in the system Python environment
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of your code into the image
COPY . .

# Expose port 8000 for the FastAPI web server
EXPOSE 8000

# Set a default command (the web server). 
# Celery commands will override this in docker-compose.yml
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]