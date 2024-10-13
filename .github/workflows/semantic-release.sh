#!/bin/bash
# Make sure packages are installed
npm install

# Determine if this is a pre-release or a release
if [[ "$1" == "pre-release" ]]; then
    RELEASE_TYPE="pre-release"
    RELEASE_BRANCH_PREFIX="rc-v"
    RELEASERC_FILE=$(pwd)/".releaserc.pre-release.js"
else
    RELEASE_TYPE="release"
    RELEASE_BRANCH_PREFIX="v"
    RELEASERC_FILE=$(pwd)/".releaserc.release.js"
fi

# Extract the new version from package.json
NEW_VERSION=$(grep '"version":' package.json | sed 's/.*"version": "\(.*\)",/\1/')
echo "New version extracted: $NEW_VERSION"

# Update the version in pyproject.toml
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS"
    sed -i '' -e "s/^version = \".*\"/version = \"$NEW_VERSION\"/" ./pyproject.toml
else
    echo "Detected Linux"
    sed -i'' -e "s/^version = \".*\"/version = \"$NEW_VERSION\"/" ./pyproject.toml
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
