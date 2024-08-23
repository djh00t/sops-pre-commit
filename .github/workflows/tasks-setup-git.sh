#!/bin/bash
# .github/workflows/tasks-setup-git.sh
###
### Setup Git & GitHub settings
###

# CMD Logger
cmd_logger() {
    local name="$1"
    local command="$2"

    if [ -z "$name" ] || [ -z "$command" ]; then
        echo "Usage: run_command <name> <command>"
        echo "  <name>: A descriptive name for the command"
        echo "  <command>: The command to run"
        return 1
    fi

    echo "Running command: $command"

    # Execute the command
    eval "$command"

    # Capture the exit status
    local status=$?

    if [ $status -eq 0 ]; then
        echo "$name succeeded ✅"
    else
        echo "$name failed with status $status ❌"
    fi

    return $status
}

# Announce start of script
echo "Setting up Git & GitHub settings"

# Authenticate GitHub CLI
cmd_logger "Authenticate GitHub CLI" "unset GH_TOKEN && echo \"${{ secrets.GITHUB_TOKEN }}\" | gh auth login --with-token"

# Configure Git & Login to GitHub CLI
cmd_logger "Configure Git & Login to GitHub CLI" "git config --global user.email \"github-actions[bot]@users.noreply.github.com\"; git config --global user.name \"github-actions[bot]\""

# Announce end of script
echo "Git & GitHub settings setup complete"
