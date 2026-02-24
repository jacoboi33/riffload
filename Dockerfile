FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# System dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-pyqt6 \
    python3-libtorrent \
    python3-lxml \
    # X11 + display libs for PyQt6 GUI
    libxcb-xinerama0 \
    libxcb-cursor0 \
    libglib2.0-0 \
    libdbus-1-3 \
    libx11-xcb1 \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip3 install --break-system-packages requests beautifulsoup4

COPY . .

# Mount point for music output
VOLUME ["/root/Music"]

CMD ["python3", "main.py"]
