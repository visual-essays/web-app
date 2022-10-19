#/bin/zsh

source .venv/bin/activate
python main.py --api http://localhost:8000 --content ../essays
