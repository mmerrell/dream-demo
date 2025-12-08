#!/bin/bash
set -e

DOCKER_REGISTRY="${2:-mmerrell}"
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "Error: Must run from main branch"
    exit 1
fi

SPRINTS=("sprint-1" "sprint-2" "sprint-3" "sprint-4" "sprint-5")

if [ -n "$1" ]; then
    if [[ ! " ${SPRINTS[@]} " =~ " $1 " ]]; then
        echo "Error: Unknown sprint: $1"
        exit 1
    fi
    SPRINTS=("$1")
fi

echo "Building sprints: ${SPRINTS[@]}"

for SPRINT in "${SPRINTS[@]}"; do
    echo "========== Building $SPRINT =========="
    
    if ! git rev-parse --verify "$SPRINT" > /dev/null 2>&1; then
        echo "Error: Branch $SPRINT does not exist"
        continue
    fi
    
    git checkout "$SPRINT"
    
    echo "Building backend..."
    docker buildx build --platform linux/amd64 -t "$DOCKER_REGISTRY/dream-demo-backend:$SPRINT" --push ./backend
    
    echo "Building frontend..."
    docker buildx build --platform linux/amd64 --build-arg REACT_APP_SPRINT_VERSION="$SPRINT" -t "$DOCKER_REGISTRY/dream-demo-frontend:$SPRINT" --push ./frontend-web
    
    echo "✓ $SPRINT complete"
done

git checkout main
echo "Done!"
