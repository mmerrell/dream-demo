# On your local machine (Mac)
for sprint in sprint-1 sprint-2 sprint-3; do
  echo "Building $sprint for AMD64..."
  git checkout $sprint
  
  # Build with platform specification for EC2 (AMD64)
  docker build --platform linux/amd64 -t mmerrell/dream-demo-frontend:$sprint ./frontend-web
  docker push mmerrell/dream-demo-frontend:$sprint
  
  docker build --platform linux/amd64 -t mmerrell/dream-demo-backend:$sprint ./backend
  docker push mmerrell/dream-demo-backend:$sprint
done

git checkout main
