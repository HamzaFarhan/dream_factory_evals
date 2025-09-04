# 1. Start the VM
ZONE="us-central1-c"
PROJECT_ID="ai-benchmarking-project"
VMNAME="appsvm2"
gcloud compute instances start $VMNAME --zone=$ZONE --project=$PROJECT_ID

# 2. Login to the VM
ZONE="us-central1-c"
PROJECT_ID="ai-benchmarking-project"
VMNAME="appsvm2"
gcloud compute ssh --zone $ZONE $VMNAME --project $PROJECT_ID

# 3. Become Root
sudo su -

# 4. Start/Stop Docker for SGLang

# Starting:
cd /opt/dream_factory_evals_app && docker-compose -f docker-compose_Qwen2.5-3B-Instruct.yaml up -d

# Stopping:
cd /opt/dream_factory_evals_app && docker-compose -f docker-compose_Qwen2.5-3B-Instruct.yaml down

# 5. Building the leaderboard image
cd /opt/dream_factory_evals_app/dream_factory_evals && docker build -t leaderboard:v1 . -f Dockerfile_leaderboard

# 6. Starting the leaderboard docker
cd /opt/dream_factory_evals_app && docker-compose -f docker-compose_leaderboard up -d

# 7. Running the uv commands from VM onto the running leaderboard docker (full list of commands is in the README.md)
cd /opt/dream_factory_evals_app

docker exec -it dream_factory_evals_app-leaderboard-1 uv run src/dream_factory_evals/run_eval.py run "Qwen2.5" hr 1

docker exec -it dream_factory_evals_app-leaderboard-1 uv run src/dream_factory_evals/run_eval.py run "openai:gpt-4.1-nano" hr 1

docker exec -it dream_factory_evals_app-leaderboard-1 uv run src/dream_factory_evals/create_leaderboard.py "hr-level-1-leaderboard" "openai:gpt-4.1-nano-hr-level-1" "Qwen/Qwen2.5-3B-Instruct-hr-level-1"  

# Saved data is on the server at location:
/opt/data/dream_factory_evals/scores/

# Stop the VM
ZONE="us-central1-c"
PROJECT_ID="ai-benchmarking-project"
VMNAME="appsvm2"
gcloud compute instances stop $VMNAME --zone=$ZONE --project=$PROJECT_ID


