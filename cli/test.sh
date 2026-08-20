#!/usr/bin/env zsh

counter=1

cleanup() {
    local sig="$1"
    echo "caught ${sig}. Quitting..."
    exit 0
}

trap 'cleanup SIGINT' INT
trap 'cleanup SIGTERM' TERM

while true; do
    echo "$counter"
    ((counter++))
    sleep 1
done
