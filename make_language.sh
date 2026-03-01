python -m manage makemessages -l de -l en -l es -l fr -l it -l nl -l pt -i ".venv*/**" -i "build/**" -e html,txt,py,js
python -m manage compilemessages -i ".venv*/**" -i "build/**"