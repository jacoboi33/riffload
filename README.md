# Riffload

Search for music albums, browse artwork, and download torrents directly to your music folder.

## Quick Start

```bash
git clone https://github.com/yourname/riffload
cd riffload
./install.sh
python3 main.py
```

## Requirements

- Python 3.10+
- Linux or macOS

## Installation

### Linux

```bash
./install.sh
```

Installs `python3-pyqt6` and `python3-libtorrent` via apt, plus pip packages.

### macOS

```bash
./install.sh
```

Requires [Homebrew](https://brew.sh). Installs `libtorrent-rasterbar` via brew and everything else via pip.

## Docker

### Linux

```bash
xhost +local:docker
docker compose up --build
```

### macOS

1. Install [XQuartz](https://www.xquartz.org)
2. Open XQuartz → Preferences → Security → check **Allow connections from network clients**
3. Restart XQuartz, then:

```bash
xhost +localhost
DISPLAY=host.docker.internal:0 docker compose up --build
```

Music is saved to `~/Music` on your host machine.

## How it works

1. Type an artist or album in the search bar
2. Album cards appear with artwork (from iTunes catalog)
3. Click an album → torrent options appear (quality, size, seeders)
4. Click **Download** → saves to `~/Music/`
