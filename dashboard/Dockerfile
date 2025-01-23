# We want to utilize the modules defined in `app/`, so we copy it to this container.

FROM --platform=linux/amd64 python:3.9

WORKDIR /dashboard

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY ../app /app

ENV PYTHONPATH=/app:/dashboard

CMD ["streamlit", "run", "Home_Page.py", "--server.port=8501", "--server.address=0.0.0.0"]
