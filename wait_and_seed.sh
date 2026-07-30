#!/bin/bash
echo "Waiting for dima-backend-core to be running..."
while true; do
  STATUS=$(docker inspect --format '{{.State.Status}}' dima-backend-core 2>/dev/null)
  if [ "$STATUS" = "running" ]; then
    echo "Container is running! Waiting 10 seconds for init..."
    sleep 10
    echo "Running seed-demo..."
    docker exec dima-backend-core python -m control_plane.cli seed-demo
    echo "Seed complete!"
    break
  fi
  sleep 5
done
