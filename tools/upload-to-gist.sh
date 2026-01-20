#!/bin/bash

# Usage: ./upload-to-gist.sh <folder_path> <gist_description> [github_token]
# Example: ./upload-to-gist.sh /path/to/folder "My EC2 files" ghp_xxxxxxxxxxxx

FOLDER_PATH="$1"
DESCRIPTION="$2"
GITHUB_TOKEN="${3:-$GITHUB_TOKEN}"

if [ -z "$FOLDER_PATH" ] || [ -z "$DESCRIPTION" ] || [ -z "$GITHUB_TOKEN" ]; then
    echo "Usage: $0 <folder_path> <description> [github_token]"
    echo "Or set GITHUB_TOKEN environment variable"
    exit 1
fi

if [ ! -d "$FOLDER_PATH" ]; then
    echo "Error: Folder $FOLDER_PATH does not exist"
    exit 1
fi

# Create temporary JSON file
TEMP_JSON=$(mktemp)
trap "rm -f $TEMP_JSON" EXIT

# Build JSON payload in temp file
echo '{"description":"'$DESCRIPTION'","public":false,"files":{' > "$TEMP_JSON"

first_file=true
while IFS= read -r -d '' file; do
    if [ -f "$file" ]; then
        relative_path="${file#$FOLDER_PATH/}"
        
        # Skip files larger than 1MB to avoid API limits
        file_size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null || echo 0)
        if [ "$file_size" -gt 1048576 ]; then
            echo "Skipping large file: $relative_path (${file_size} bytes)"
            continue
        fi
        
        if [ "$first_file" = true ]; then
            first_file=false
        else
            echo ',' >> "$TEMP_JSON"
        fi
        
        echo -n '"'$relative_path'":{"content":"' >> "$TEMP_JSON"
        cat "$file" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g' >> "$TEMP_JSON"
        echo -n '"}' >> "$TEMP_JSON"
    fi
done < <(find "$FOLDER_PATH" -type f -print0)

echo '}}' >> "$TEMP_JSON"

# Upload to Gist using temp file
response=$(curl -s -X POST \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
    -d @"$TEMP_JSON" \
    https://api.github.com/gists)

# Extract and display Gist URL
gist_url=$(echo "$response" | grep -o '"html_url":"[^"]*' | cut -d'"' -f4)

if [ -n "$gist_url" ]; then
    echo "Gist created successfully: $gist_url"
else
    echo "Error creating Gist:"
    echo "$response"
    exit 1
fi
