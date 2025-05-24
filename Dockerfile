# Use an official Python image
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

EXPOSE 4000

CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "app.py"]