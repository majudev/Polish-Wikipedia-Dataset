#!/bin/bash
cd "$(dirname "$0")"

OUTPUT_DIRECTORY_NAME="output"

if [ -e output ]; then
	echo "Removing output directory"
	rm -r $OUTPUT_DIRECTORY_NAME
fi
mkdir output

. venv/bin/activate
python3 main.py --output "`pwd`/$OUTPUT_DIRECTORY_NAME"
