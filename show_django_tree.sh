#!/bin/bash

# Define the project root directory
PROJECT_ROOT="$(pwd)"

# Define the list of target files
TARGET_FILES=(
    "models.py"
    "serializers.py"
    "views.py"
    "tools.sh"
    "supervisord.py"
    "Dockerfile"
    "settings.py"
    "init_database.sh"
    "run_consumer.sh"
    "requirements.txt"
    "consumer.py"
    "rabbitmq_utils.py"
    "user_session_views.py"
    "validators.py"
    "signals.py"
    "consumers.py"
    "asgi.py"
    "apps.py"
    "urls.py"
    "asgi.py"
    "wsgi.py"
    "*.yml"
    "*.conf"
    "*.ini"
    "*.env"
    "*.sh"

)

# Function to print the directory tree with an arrow
print_tree_with_arrows() {
    local prefix="$1"
    local dir="$2"
    local depth="$3"

    # Print the current directory
    echo "${prefix}$(basename "$dir")"

    # Iterate over all items in the directory
    for item in "$dir"/*; do
        if [ -d "$item" ]; then
            # Recurse into directories
            print_tree_with_arrows "$prefix--> " "$item" "$((depth + 1))"
        elif [ -f "$item" ]; then
            # Print files
            echo "${prefix}--> $(basename "$item")"
        fi
    done
}

# Function to print the path and content of the target files
print_file_contents() {
    local file="$1"
    if [ -f "$file" ]; then
        echo -e "\nPath: $file"
        echo "Directory Tree:"
        local dir=$(dirname "$file")
        print_tree_with_arrows "" "$dir" 0
        echo -e "\nContent of $(basename "$file"):"
        cat "$file"
    fi
}

# Print the full project tree
echo "Full Project Tree:"
tree -a

# Print the path and content of each target file
for target_file in "${TARGET_FILES[@]}"; do
    find "$PROJECT_ROOT" -name "$target_file" -type f | while read -r file; do
        print_file_contents "$file"
    done
done
