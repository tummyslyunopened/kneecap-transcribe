mkdir -p ./logs
uv run main.py > ./logs/runserver-output.log 2> ./logs/runserver-error.log &
tail -f ./logs/runserver-output.log ./logs/runserver-error.log
