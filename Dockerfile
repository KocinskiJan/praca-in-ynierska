# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Install build dependencies for USalign
RUN apt-get update && apt-get install -y \
    g++ \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Download and compile USalign
WORKDIR /tmp
RUN wget https://zhanggroup.org/US-align/bin/module/USalign.cpp && \
    g++ -static -O3 -ffast-math -o USalign USalign.cpp && \
    mv USalign /usr/local/bin/ && \
    rm USalign.cpp

# Set the working directory in the container
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy all Python scripts and other files
COPY inf.py /app/
COPY lddt.py /app/
COPY mcq.py /app/
COPY rmsd.py /app/
COPY tm_score.py /app/
COPY torsion.py /app/

# Make all scripts executable
RUN chmod +x /app/*.py

# Set environment variable for scripts location
ENV PATH="/app:${PATH}"

# Default command (can be overridden)
CMD ["python", "-c", "import sys; print('Available scripts: clashscore.py, inf.py, lddt.py, mcq.py, rmsd.py, tm_score.py, torsion.py')"]