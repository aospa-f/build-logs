#!/usr/bin/env bash
#
# setup_fresh_server.sh
# Sets up a fresh Linux / ServerHive Ubuntu environment for building AOSPA.
#
set -euo pipefail

echo "[+] Preparing system packages for Android ROM building..."

if [ "$EUID" -ne 0 ]; then
    SUDO="sudo"
else
    SUDO=""
fi

$SUDO apt-get update -y

# Core build tools, python, clang/gcc headers, and kernel requirements (pahole, libelf, libssl)
$SUDO apt-get install -y \
    bc \
    bison \
    build-essential \
    ccache \
    curl \
    dwarves \
    flex \
    g++-multilib \
    gcc-multilib \
    git \
    git-lfs \
    gnupg \
    gperf \
    imagemagick \
    jq \
    lib32ncurses5-dev \
    lib32readline-dev \
    lib32z1-dev \
    libelf-dev \
    liblz4-tool \
    libncurses5 \
    libncurses5-dev \
    libsdl1.2-dev \
    libssl-dev \
    libxml2 \
    libxml2-utils \
    lzop \
    ninja-build \
    pahole \
    pngcrush \
    python3 \
    python3-pip \
    rsync \
    schedtool \
    squashfs-tools \
    xsltproc \
    zip \
    zlib1g-dev

# Ensure git-lfs is installed
git lfs install || true

# Install or update repo launcher
if ! command -v repo >/dev/null 2>&1; then
    echo "[+] Installing Google repo tool..."
    $SUDO curl -s https://storage.googleapis.com/git-repo-downloads/repo > /usr/local/bin/repo
    $SUDO chmod a+rx /usr/local/bin/repo
fi

# Configure Git user identity if not already set
if [ -z "$(git config --global user.name || true)" ]; then
    echo "[+] Configuring git username (dyruz10)..."
    git config --global user.name "dyruz10"
fi
if [ -z "$(git config --global user.email || true)" ]; then
    echo "[+] Configuring git email (lucykushinay@gmail.com)..."
    git config --global user.email "lucykushinay@gmail.com"
fi
git config --global color.ui auto

# Configure CCache
echo "[+] Configuring ccache to 100GB..."
ccache -M 100G || true
mkdir -p ~/.ccache

# Add environment variables to ~/.bashrc if not already present
if ! grep -q "USE_CCACHE" ~/.bashrc 2>/dev/null; then
    cat << 'EOF' >> ~/.bashrc

# Android Build Environment Configuration
export USE_CCACHE=1
export CCACHE_EXEC=$(which ccache)
export CCACHE_DIR=$HOME/.ccache
EOF
fi

echo "[✓] Fresh server environment setup complete!"
