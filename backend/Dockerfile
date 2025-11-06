FROM python:3.9-slim

WORKDIR /app

# Copy and install requirements
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
# In development, this will be overwritten by the volume mount
COPY app/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]