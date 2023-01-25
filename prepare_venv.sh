#!/bin/bash
cd "$(dirname "$0")"

if [ ! -d venv ]; then
	echo "Creating venv"
	python3 -m venv venv
else
	echo "Python venv already exists. To remove it, use: rm -r venv"
fi
. venv/bin/activate
pip install -U pip
pip install -r requirements.txt
echo "Done"
