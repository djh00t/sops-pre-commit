#!/bin/bash
# .github/workflows/tasks-setup-variables.sh
###
### Setup variables for github actions workflows
###

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

# Make sure $WORKFLOW_STAGE is set and isn't blank
if [ -z "$WORKFLOW_STAGE" ]; then
    echo "Stage input variable is not set. Exiting..."
    exit 1
fi

# Announce start of script
echo "Setting up variables for stage: $WORKFLOW_STAGE"

# Setup the BRANCH_BASE variable
cmd_logger "Setup the BRANCH_BASE variable" "export BRANCH_BASE=$WORKFLOW_STAGE"

# Capitalise first char of $BRANCH_BASE and export as $WORKFLOW_STAGE_CAP
cmd_logger "Capitalise first char of $BRANCH_BASE" "export WORKFLOW_STAGE_CAP=$(echo "$BRANCH_BASE" | awk '{print toupper(substr($0, 1, 1)) tolower(substr($0, 2))}')"

# Setup current branch name variable
cmd_logger "Setup current branch name variable" "export BRANCH_CURRENT=$(git rev-parse --abbrev-ref HEAD)"

# Check if the current branch has a PR associated with it
cmd_logger "Check if the current branch has a PR associated with it" "export PR_EXISTS=$(gh pr list --json number --jq '.[0].number' || echo "")"

# If a PR exists, get the PR number
if [ -n "$PR_EXISTS" ]; then
    cmd_logger "Getting the PR number" "export PR_NUMBER=$(gh pr list --json number --jq '.[0].number')"
fi

# If a PR exists, get the PR URL
if [ -n "$PR_EXISTS" ]; then
    cmd_logger "Getting the PR URL" "export PR_URL=$(gh pr view $PR_NUMBER --json url --jq '.url')"
fi

# If a PR exists, get the PR title and remove problematic characters
if [ -n "$PR_EXISTS" ]; then
    cmd_logger "Getting the PR title" "export PR_TITLE=$(gh pr view $PR_NUMBER --json title --jq '.title')"
fi

# Log PR details if a PR exists
if [ -n "$PR_EXISTS" ]; then
    echo "PR $PR_NUMBER exists for this branch: $BRANCH_CURRENT"
    echo "PR $PR_NUMBER title is: $PR_TITLE"
    echo "PR $PR_NUMBER URL is: $PR_URL"
fi

# Echo end of script
echo "Variables setup complete"
