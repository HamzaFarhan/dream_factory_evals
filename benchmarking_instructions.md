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
## the name of the sglang model does not matter. you can pass in any name you want since there will be only one model running at a time.

cd /opt/dream_factory_evals_app

docker exec -it dream_factory_evals_app-leaderboard-1 uv run src/dream_factory_evals/run_eval.py run "qwen2-5" hr 1

docker exec -it dream_factory_evals_app-leaderboard-1 uv run src/dream_factory_evals/run_eval.py run "openai:gpt-4.1-nano" hr 1

docker exec -it dream_factory_evals_app-leaderboard-1 uv run src/dream_factory_evals/create_leaderboard.py "hr-level-1-leaderboard" "openai:gpt-4.1-nano-hr-level-1" "qwen2-5-hr-level-1"  

## Saved data is on the server at location:
/opt/data/dream_factory_evals/scores/

# Change the SGLang model

## 1. Stop the docker
cd /opt/dream_factory_evals_app && docker-compose -f docker-compose_Qwen2.5-3B-Instruct.yaml down

## 2. Make a copy of the docker-compose_Qwen2.5-3B-Instruct.yaml file
cp docker-compose_Qwen2.5-3B-Instruct.yaml docker-compose_Qwen3-8B.yaml

## 3. Change the first 4 lines:

Change the --model-path and --tool-call-parser:

services:
  sglang-server-Qwen2.5-3B-Instruct:
    image: lmsysorg/sglang:v1
    command: python3 -m sglang.launch_server --model-path Qwen/Qwen2.5-3B-Instruct --tool-call-parser qwen25 --host 0.0.0.0 --port 30000
    ...

to:

services:
  sglang-server-Qwen3-8B:
    image: lmsysorg/sglang:v1
    command: python3 -m sglang.launch_server --model-path Qwen/Qwen3-8B --tool-call-parser qwen3 --host 0.0.0.0 --port 30000
    ...

## 4. Start the docker
cd /opt/dream_factory_evals_app && docker-compose -f docker-compose_Qwen3-8B.yaml up -d

## 5. Run the uv commands from VM onto the running leaderboard docker (full list of commands is in the README.md)
## the name of the sglang model does not matter. you can pass in any name you want since there will be only one model running at a time.

cd /opt/dream_factory_evals_app

docker exec -it dream_factory_evals_app-leaderboard-1 uv run src/dream_factory_evals/run_eval.py run "qwen3-8b" hr 1

# Remember to stop the VM when you are done to save costs.
ZONE="us-central1-c"
PROJECT_ID="ai-benchmarking-project"
VMNAME="appsvm2"
gcloud compute instances stop $VMNAME --zone=$ZONE --project=$PROJECT_ID