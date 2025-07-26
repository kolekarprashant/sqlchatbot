FROM python:3.11-slim

WORKDIR /app

# Copy app files
COPY . .

# Install requirements
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 5000
EXPOSE 8000

# Run both Flask and FastAPI using a process manager
# Option 1: Use a script to launch both
CMD ["sh", "-c", "python flask_ui/app.py & uvicorn fast_api.main:app --host 0.0.0.0 --port 8000"]
