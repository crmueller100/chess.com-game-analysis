FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app:/dashboard

# This runs the script that queries the API, saves the data, and loads it into the database
# CMD ["python", "main.py"]

# This is used to keep the container running. Useful for entering Docker container for development and testing
ENTRYPOINT ["tail", "-f", "/dev/null"]
