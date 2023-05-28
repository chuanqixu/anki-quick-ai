#!/bin/bash
FILE="anki_quick_ai.ankiaddon"

# Check if the file exists
if [ -f "$FILE" ]; then
    echo "$FILE exists, removing..."
    rm $FILE
fi

# remove unnecessory files
find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf
rm -r output

# Zip all files excluding meta.json into anki_quick_ai.ankiaddon
zip -r $FILE * -x "meta.json"
