# For each sprint
for sprint in sprint-1 sprint-2 sprint-3; do
  echo "Building $sprint..."
  git checkout $sprint
  
  docker build -t mmerrell/dream-demo-frontend:$sprint ./frontend-web
  docker push mmerrell/dream-demo-frontend:$sprint
  
  docker build -t mmerrell/dream-demo-backend:$sprint ./backend  
  docker push mmerrell/dream-demo-backend:$sprint
done

git checkout main
