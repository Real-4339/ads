FROM python:3.12.10-slim

# Set the working directory
WORKDIR /app

# 3. Install system dependencies
#    build-essential - enable gcc, g++, etc.
#    python3-dev - enable Python headers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY ./ads/ci/requirements.txt .

# 4. Install the Python dependencies
# --no-cache-dir - to avoid caching the packages in the image
# --upgrade pip - recommended to ensure the latest version of pip is used
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY ./ads .

CMD [ "python", "-m", "ads" ]