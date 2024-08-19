# Stage 1: Build Stage
FROM python:3.11-slim AS builder

# Set working directory in the container
WORKDIR /app

# Copy only requirements to leverage Docker layer caching
COPY requirements.txt .

# Create a virtual environment and activate it
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# cmake required for dlib
# Install necessary build tools and libraries
RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install project dependencies within the virtual environment
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production Stage
FROM python:3.11-slim AS production

# Installing make libgl
RUN apt update && apt upgrade -y && apt install -y \
    make \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory in the container
WORKDIR /app

# Copy only necessary files from the builder stage, including the virtual environment
COPY --from=builder /opt/venv /opt/venv
COPY . .

# Set the environment variable to use the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# install ai service
RUN make install

# Expose the port where the FastAPI app will run
EXPOSE 8000

# run the service using the cli
CMD ["inteliver", "run"]