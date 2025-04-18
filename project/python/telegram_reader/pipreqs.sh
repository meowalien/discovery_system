pipreqs ./ --force --ignore .venv,__pycache__,build,dist
awk '!seen[$0]++' requirements.txt > tmp && mv tmp requirements.txt