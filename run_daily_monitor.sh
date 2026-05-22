#!/bin/bash

cd ~/Documents/aspect-hpc-ai-monitor/aspect-hpc-ai-monitor

export HPC_HOST=fir.computecanada.ca
export HPC_USERNAME=ajbaruah
export HPC_SSH_KEY=$HOME/.ssh/id_ed25519
export OPENAI_API_KEY="YOUR_API_PASSWORD"

export EMAIL_USER="lbaruah51@gmail.com"
export EMAIL_PASSWORD="YOUR_GMAIL_PASSWORD"
export EMAIL_TO="lbaruah51@gmail.com"

python3 monitor.py remote-log \
--path /home/ajbaruah/scratch/ajbaruah/Two_sided_subduction_test_2/log.txt \
--ai
