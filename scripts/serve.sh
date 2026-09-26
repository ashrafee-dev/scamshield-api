#!/bin/sh
set -eu
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1 \
    --no-proxy-headers --no-access-log --limit-concurrency 32 \
    --timeout-keep-alive 5 --ws websockets --ws-per-message-deflate false \
    --ws-max-size "${MAX_FILE_SIZE:-26214400}" --ws-max-queue 1
