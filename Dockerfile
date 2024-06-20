FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project code into the container
COPY . .

# Set the command to run when the container starts
# ENTRYPOINT [ "bash" ]  

# CMD [ "python", "src/get_player_data.py"]
CMD ["python", "main.py"]
