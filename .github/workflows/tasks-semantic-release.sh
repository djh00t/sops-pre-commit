#!/bin/bash



# CMD Logger
cmd_logger() {
    local name="$1"
    local command="$2"
    local msg_success="$3"
    local msg_fail="$4"

    if [ -z "$name" ] || [ -z "$command" ]; then
        echo "Usage: run_command <name> <command> [msg_success] [msg_fail]"
        echo "  <name>: A descriptive name for the command"
        echo "  <command>: The command to run"
        echo "  [msg_success]: Optional custom success message"
        echo "  [msg_fail]: Optional custom fail message"
        return 1
    fi

    echo "Running command: $command"

    # Execute the command
    eval "$command"

    # Capture the exit status
    local status=$?

    if [ $status -eq 0 ]; then
        if [ -n "$msg_success" ]; then
            echo "$msg_success ✅"
        else
            echo "$name succeeded ✅"
        fi
    else
        if [ -n "$msg_fail" ]; then
            echo "$msg_fail ❌"
        else
            echo "$name failed with status $status ❌"
        fi
    fi

    return $status
}

# Determine if this is a pre-release or a release
if [[ "$1" == "pre-release" ]]; then
    RELEASE_TYPE="pre-release"
    RELEASE_BRANCH_PREFIX="rc-v"
    RELEASERC_FILE=".releaserc-pre-release.js"
elif [[ "$1" == "release" ]]; then
    RELEASE_TYPE="release"
    RELEASE_BRANCH_PREFIX="v"
    RELEASERC_FILE=".releaserc-release.js"
else
    echo "Invalid release type. Exiting..."
    exit 1
fi

# Extract the new version from package.json
NEW_VERSION=$(grep '"version":' package.json | sed 's/.*"version": "\(.*\)",/\1/')
echo "New version extracted: $NEW_VERSION"

# Function to check if a tag exists
tag_exists() {
    git fetch --tags
    git tag -l | grep -q "^$1$"
}

# Increment version function
increment_version() {
    local version=$1
    local major=$(echo $version | cut -d. -f1)
    local minor=$(echo $version | cut -d. -f2)
    local patch=$(echo $version | cut -d. -f3)
    patch=$((patch + 1))
    echo "$major.$minor.$patch"
}

# Check for version conflicts and increment if necessary
while tag_exists "v$NEW_VERSION"; do
    echo "Version $NEW_VERSION already exists. Incrementing version..."
    NEW_VERSION=$(increment_version $NEW_VERSION)
    echo "New incremented version: $NEW_VERSION"
done

# Update the version in package.json
jq --arg new_version "$NEW_VERSION" '.version = $new_version' package.json > tmp.$$.json && mv tmp.$$.json package.json

# Extract the new description from package.json
NEW_DESCRIPTION=$(grep '"description":' package.json | sed 's/.*"description": "\(.*\)",/\1/')
echo "New description extracted: $NEW_DESCRIPTION"

# Update the version and description in pyproject.toml
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS"
    sed -i '' -e "s/^version = \".*\"/version = \"$NEW_VERSION\"/" ./pyproject.toml
    sed -i '' -e "s/^description = \".*\"/description = \"$NEW_DESCRIPTION\"/" ./pyproject.toml
else
    echo "Detected Linux"
    sed -i'' -e "s/^version = \".*\"/version = \"$NEW_VERSION\"/" ./pyproject.toml
    sed -i'' -e "s/^description = \".*\"/description = \"$NEW_DESCRIPTION\"/" ./pyproject.toml
fi

# Update the version in package.json
jq --arg new_version "$NEW_VERSION" '.version = $new_version' package.json > tmp.$$.json && mv tmp.$$.json package.json

# Replace the placeholder in pyproject.toml
sed -i'' -e "s/\${nextRelease.version}/$NEW_VERSION/g" pyproject.toml

# Run semantic-release with the appropriate configuration file
echo "Running semantic-release with $RELEASERC_FILE..."
npx semantic-release --extends $RELEASERC_FILE

# If semantic-release was successful, commit the changes to a new branch
if [ $? -eq 0 ]; then
    git checkout -b ${RELEASE_BRANCH_PREFIX}$NEW_VERSION
    git add pyproject.toml
    git commit -m "chore: update pyproject.toml to $NEW_VERSION [skip ci]"
    git push origin ${RELEASE_BRANCH_PREFIX}$NEW_VERSION
else
    echo "semantic-release failed"
fi
