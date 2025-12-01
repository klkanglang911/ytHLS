# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

# * Docker İmajı
FROM python:3.11.8-slim-bookworm

# * Python Standart Değişkenler
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONIOENCODING="UTF-8"

# * Dil ve Bölge
ENV LANGUAGE="tr_TR.UTF-8" LANG="tr_TR.UTF-8" LC_ALL="tr_TR.UTF-8" TZ="Europe/Istanbul"

# * Çalışma Alanı
WORKDIR /usr/src/ythls-FastAPI
COPY ./ /usr/src/ythls-FastAPI

# ? Sistem Kurulumları ve Gereksiz Dosyaların Silinmesi
RUN apt-get update -y && \
    apt-get install --no-install-recommends -y \
        # git \
        # ffmpeg \
        # opus-tools \
        locales && \
    sed -i -e 's/# tr_TR.UTF-8 UTF-8/tr_TR.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# * Gerekli Paketlerin Yüklenmesi
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install --no-cache-dir -U setuptools wheel && \
    python3 -m pip install --no-cache-dir -Ur requirements.txt

# * Python Çalıştırılması
# Copy cookies.txt to writable location at startup to prevent yt-dlp from corrupting the mounted file
CMD ["sh", "-c", "cp -f /usr/src/ythls-FastAPI/cookies.txt /tmp/cookies.txt 2>/dev/null || true; python3 basla.py"]