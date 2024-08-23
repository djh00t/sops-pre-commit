#!/bin/bash
# .github/workflows/tasks-pr-create-update.sh
###
### Create or update a PR
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

# Announce start of script
echo "Starting PR Create/Update"

# Generate current $PR_BODY and export it as an environment variable
cmd_logger "Generate current PR Body merging $BRANCH_CURRENT into $BRANCH_BASE" "export PR_BODY=\"$(poetry run python3 .github/workflows/pr_body_gen.py $BRANCH_CURRENT $BRANCH_BASE)\""

# EXISTING PR: Update PR body
if [ -n "$PR_EXISTS" ]; then
    echo "PR Exists: $PR_EXISTS"
    # Update PR with current body
    poetry run gh pr edit $PR_URL --title "$PR_TITLE" --body "$PR_BODY"
fi

# NEW PR: Generate PR Title & create new PR
if [ -z "$PR_EXISTS" ]; then
    echo "PR does not exist, creating new PR.."
    # Generate PR Title
    cmd_logger "Generating PR Title" "export PR_TITLE=$(pr-title-generate)"

    # Create PR,  if it ends successfully otherwise echo an error.
    cmd_logger "Creating PR" "PR_URL=$(poetry run gh pr create --title \"$PR_TITLE\" --body \"$PR_BODY\" --base $BRANCH_BASE --head $BRANCH_CURRENT) || echo \"Failed to create PR\"" "echo \"PR Created: $PR_URL\""
fi
