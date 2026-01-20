#!/bin/bash

# Usage: ./upload-to-repo.sh <folder_path> <github_user> <repo_name> <branch> [github_token]
# Example: ./upload-to-repo.sh /path/to/folder myuser myrepo main ghp_xxxxxxxxxxxx

FOLDER_PATH="$1"
GITHUB_USER="$2"
REPO_NAME="$3"
BRANCH="$4"
GITHUB_TOKEN="${5:-$GITHUB_TOKEN}"

if [ -z "$FOLDER_PATH" ] || [ -z "$GITHUB_USER" ] || [ -z "$REPO_NAME" ] || [ -z "$BRANCH" ] || [ -z "$GITHUB_TOKEN" ]; then
    echo "Usage: $0 <folder_path> <github_user> <repo_name> <branch> [github_token]"
    echo "Or set GITHUB_TOKEN environment variable"
    exit 1
fi

if [ ! -d "$FOLDER_PATH" ]; then
    echo "Error: Folder $FOLDER_PATH does not exist"
    exit 1
fi

API_BASE="https://api.github.com/repos/$GITHUB_USER/$REPO_NAME"

# Check if repo exists
echo "Checking repository access..."
repo_check=$(curl -s -H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2022-11-28" -H "Authorization: token $GITHUB_TOKEN" "$API_BASE")
if echo "$repo_check" | grep -q '"message":"Not Found"'; then
    echo "Error: Repository $GITHUB_USER/$REPO_NAME not found or no access"
    exit 1
fi

# Get latest commit SHA
echo "Getting latest commit SHA for branch $BRANCH..."
ref_response=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    "$API_BASE/git/refs/heads/$BRANCH")

latest_sha=$(echo "$ref_response" | grep -o '"sha":"[^"]*' | cut -d'"' -f4)

if [ -z "$latest_sha" ]; then
    echo "Branch '$BRANCH' not found. Checking if repo is empty..."
    
    # Check if repo has any commits
    commits_response=$(curl -s -H "Authorization: token $GITHUB_TOKEN" "$API_BASE/commits")
    
    if echo "$commits_response" | grep -q '"message":"Git Repository is empty"'; then
        echo "Repository is empty. Creating initial commit..."
        
        # Create initial empty tree
        empty_tree_response=$(curl -s -X POST \
            -H "Authorization: token $GITHUB_TOKEN" \
            -H "Content-Type: application/json" \
            -d '{"tree":[]}' \
            "$API_BASE/git/trees")
        
        empty_tree_sha=$(echo "$empty_tree_response" | grep -o '"sha":"[^"]*' | cut -d'"' -f4)
        
        # Create initial commit
        initial_commit_response=$(curl -s -X POST \
            -H "Authorization: token $GITHUB_TOKEN" \
            -H "Content-Type: application/json" \
            -d '{"message":"Initial commit","tree":"'$empty_tree_sha'"}' \
            "$API_BASE/git/commits")
        
        latest_sha=$(echo "$initial_commit_response" | grep -o '"sha":"[^"]*' | cut -d'"' -f4)
        
        # Create branch reference
        curl -s -X POST \
            -H "Authorization: token $GITHUB_TOKEN" \
            -H "Content-Type: application/json" \
            -d '{"ref":"refs/heads/'$BRANCH'","sha":"'$latest_sha'"}' \
            "$API_BASE/git/refs" > /dev/null
        
        echo "Created initial branch: $BRANCH"
    else
        echo "Available branches:"
        curl -s -H "Authorization: token $GITHUB_TOKEN" \
            "$API_BASE/branches" | grep -o '"name":"[^"]*' | cut -d'"' -f4
        echo ""
        echo "Use existing branch name"
        exit 1
    fi
fi

echo "Latest commit SHA: $latest_sha"

# Create blobs for each file
declare -A file_shas
while IFS= read -r -d '' file; do
    if [ -f "$file" ]; then
        relative_path="${file#$FOLDER_PATH/}"

        # Skip files larger than 100MB (GitHub limit)
        file_size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null || echo 0)
        if [ "$file_size" -gt 104857600 ]; then
            echo "Skipping large file: $relative_path (${file_size} bytes)"
            continue
        fi

        echo "Processing: $relative_path"

        # Create blob
        content_base64=$(base64 -w 0 "$file")
        blob_response=$(curl -s -X POST \
            -H "Authorization: token $GITHUB_TOKEN" \
            -H "Content-Type: application/json" \
            -d '{"content":"'$content_base64'","encoding":"base64"}' \
            "$API_BASE/git/blobs")

        blob_sha=$(echo "$blob_response" | grep -o '"sha":"[^"]*' | cut -d'"' -f4)
        if [ -n "$blob_sha" ]; then
            file_shas["$relative_path"]="$blob_sha"
        else
            echo "Error creating blob for $relative_path"
        fi
    fi
done < <(find "$FOLDER_PATH" -type f -print0)

# Create tree
TEMP_TREE=$(mktemp)
trap "rm -f $TEMP_TREE" EXIT

echo '{"tree":[' > "$TEMP_TREE"
first_entry=true
for file_path in "${!file_shas[@]}"; do
    if [ "$first_entry" = true ]; then
        first_entry=false
    else
        echo ',' >> "$TEMP_TREE"
    fi
    echo '{"path":"'$file_path'","mode":"100644","type":"blob","sha":"'${file_shas[$file_path]}'"}' >> "$TEMP_TREE"
done
echo ']}' >> "$TEMP_TREE"

tree_response=$(curl -s -X POST \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
    -d @"$TEMP_TREE" \
    "$API_BASE/git/trees")

tree_sha=$(echo "$tree_response" | grep -o '"sha":"[^"]*' | cut -d'"' -f4)

if [ -z "$tree_sha" ]; then
    echo "Error creating tree"
    exit 1
fi

echo "Tree SHA: $tree_sha"

# Create commit
commit_message="Upload folder: $(basename "$FOLDER_PATH")"
commit_response=$(curl -s -X POST \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"message":"'$commit_message'","tree":"'$tree_sha'","parents":["'$latest_sha'"]}' \
    "$API_BASE/git/commits")

commit_sha=$(echo "$commit_response" | grep -o '"sha":"[^"]*' | cut -d'"' -f4)

if [ -z "$commit_sha" ]; then
    echo "Error creating commit"
    exit 1
fi

echo "Commit SHA: $commit_sha"

# Update branch reference
update_response=$(curl -s -X PATCH \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"sha":"'$commit_sha'"}' \
    "$API_BASE/git/refs/heads/$BRANCH")

if echo "$update_response" | grep -q '"ref":'; then
    echo "Successfully uploaded folder to https://github.com/$GITHUB_USER/$REPO_NAME/tree/$BRANCH"
else
    echo "Error updating branch reference"
    echo "$update_response"
    exit 1
fi
