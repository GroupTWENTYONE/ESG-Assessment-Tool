docker compose down
docker volume ls -q | grep -v esg-assessment-tool_ollama_data | xargs -r docker volume rm # delete every volume except ollama volume (prevents long download for development purposes)
docker compose up --build -d 
docker exec ollama ollama pull llama3-groq-tool-use:8b