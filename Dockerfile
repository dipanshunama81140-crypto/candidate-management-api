# 1. Official lightweight Python runtime
FROM python:3.12-slim

# 2. Container ke andar working directory set karein
WORKDIR /app

# 3. Python environment optimization (Buffer off, no bytecode written to disk)
ENV PYTHONDONTWRITBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 4. Dependencies install karein
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Saara project code container ke andar copy karein
COPY . .

# 6. Port expose karein
EXPOSE 8000

# 7. FastAPI server run karein
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]