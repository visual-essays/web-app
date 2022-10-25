#/bin/zsh

#/bin/zsh

cd "$(dirname "$0")"

source .venv/bin/activate
python main.py --api http://localhost:8000 --content ../essays
