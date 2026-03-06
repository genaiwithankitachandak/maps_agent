# maps_agent
Agent suggesting places with Google maps grounding and use preference

start backend:
uvicorn main:app --port 8080 --reload

start frontend:
cd frontend && source ~/.nvm/nvm.sh && npm run dev
source ~/.nvm/nvm.sh && npm run dev -- --host

kill service:
lsof -ti :8080 | xargs kill -9 

run frontend locally:
cd frontend
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use node
npm run build
npm run dev