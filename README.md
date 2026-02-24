# Riffload

Search for music albums, browse artwork, and download torrents directly to your music folder.

![Riffload](assets/logo.png)

---

## Install & Run

### Linux (Ubuntu, Debian, Pop!_OS, Arch, Manjaro, Fedora)

Open a terminal and paste this:

```bash
git clone https://github.com/jacoboi33/riffload
cd riffload
./install.sh
```

Then launch it:

```bash
riffload
```

Or find **Riffload** in your app launcher.

---

### macOS

Make sure you have [Homebrew](https://brew.sh) installed first, then:

```bash
git clone https://github.com/jacoboi33/riffload
cd riffload
./install.sh
```

Then launch it:

```bash
riffload
```

> **Note:** If `riffload` isn't found after install, open a new terminal window and try again.

---

### Docker (any OS)

**Linux:**
```bash
git clone https://github.com/jacoboi33/riffload
cd riffload
xhost +local:docker
docker compose up --build
```

**macOS:**
1. Install [XQuartz](https://www.xquartz.org)
2. Open XQuartz → Preferences → Security → check **Allow connections from network clients**
3. Restart XQuartz, then:

```bash
git clone https://github.com/jacoboi33/riffload
cd riffload
xhost +localhost
DISPLAY=host.docker.internal:0 docker compose up --build
```

Music downloads are saved to `~/Music` on your machine.

---

## Requirements

- Git
- Python 3.10+
- Linux, macOS, or Docker

---

## How it works

1. Type an artist or album in the search bar
2. Album cards appear with artwork
3. Click an album → see available torrents (quality, size, seeders)
4. Click **Download** → saves to `~/Music/`

Searches across: The Pirate Bay, 1337x, Nyaa, TorrentGalaxy, BitSearch, and KickassTorrents — all at the same time.
