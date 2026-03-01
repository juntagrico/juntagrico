python -m manage makemessages --all -i ".venv*/**" -i "build/**" -e html,txt,py,js
python -m manage compilemessages -i ".venv*/**" -i "build/**"