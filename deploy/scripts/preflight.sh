#!/usr/bin/env sh
set -eu

echo "Numra read-only host preflight"
printf "OS: "
. /etc/os-release
echo "${PRETTY_NAME:-unknown}"
printf "Kernel: "
uname -r
printf "Architecture: "
uname -m
printf "CPU cores: "
getconf _NPROCESSORS_ONLN
printf "Memory: "
awk '/MemTotal/ { printf "%.1f GiB\n", $2 / 1024 / 1024 }' /proc/meminfo
printf "Free space at /opt: "
df -hP /opt | awk 'NR == 2 { print $4 }'
printf "Docker: "
docker --version
printf "Compose: "
docker compose version

echo "Listeners relevant to Numra:"
ss -ltn | awk 'NR == 1 || $4 ~ /:(80|443|8080)$/'

echo "Required checks:"
echo "- Ubuntu 24.04 LTS or explicitly approved equivalent"
echo "- at least 40 GiB free at /opt"
echo "- Docker Engine with Compose v2+"
echo "- 127.0.0.1:8080 free"
