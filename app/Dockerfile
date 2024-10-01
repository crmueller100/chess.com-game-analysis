FROM python:3.9

WORKDIR /app

# Install Java
RUN apt-get update && \
    apt-get install -y default-jdk && \
    apt-get clean

# Set JAVA_HOME environment variable
ENV JAVA_HOME /usr/lib/jvm/default-java
ENV PATH $JAVA_HOME/bin:$PATH

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app:/dashboard

# Change the path to the Stockfish binary to match the path in the container
ENV STOCKFISH_PATH /usr/local/bin/stockfish/stockfish-android-armv8

# This is used to keep the container running. Useful for entering Docker container for development and testing
ENTRYPOINT ["tail", "-f", "/dev/null"]
