# Dockerfile

# 1. Choose a lightweight Python image
FROM python:3.12-slim

# 2. Set work directory
WORKDIR /app

# 3. Copy requirements
COPY requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN ls - al
# 5. Copy the entire project
COPY . .

# 6. Expose FastAPI port
EXPOSE 8000

# 7. Start FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
