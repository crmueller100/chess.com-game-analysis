# Need to use an architecture that is compatible with ECS
FROM --platform=linux/amd64 python:3.9

# Install Java for Spark
# RUN apt-get update && \
#     apt-get install -y default-jdk && \
#     apt-get clean
# ENV JAVA_HOME /usr/lib/jvm/default-java
# ENV PATH $JAVA_HOME/bin:$PATH

WORKDIR /dashboard

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# I build the dashboard image for AWS ECR from the root directory of the project and by doing `docker build -t image -f dashboard/Dockerfile .`
COPY . .
COPY ../app /app

ENV PYTHONPATH=/app:/dashboard

# Change the path to the Stockfish binary to match the path in the container
ENV STOCKFISH_PATH /usr/local/bin/stockfish/stockfish-android-armv8

CMD ["streamlit", "run", "dashboard/Home_Page.py", "--server.port=8501", "--server.address=0.0.0.0"]
