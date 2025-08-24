#!/bin/zsh

# Rename all .md files to .txt in the current directory
for file in *.md; do
    if [[ -f "$file" ]]; then
        newfile="${file%.md}.txt"
        if [[ -e "$newfile" ]]; then
            echo "Warning: $newfile already exists. Skipping $file."
        else
            mv "$file" "$newfile"
            echo "Renamed $file to $newfile"
        fi
    fi
done