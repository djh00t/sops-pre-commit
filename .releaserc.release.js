module.exports = {
  branches: [{ name: "release", prerelease: false }],
  repositoryUrl: "https://github.com/djh00t/sops-pre-commit.git",
  plugins: [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    "@semantic-release/changelog",
    [
      "@semantic-release/github",
      {
        assets: [{ path: "dist/**", label: "Distribution" }],
        successComment: false,
        failComment: false,
      },
    ],
    [
      "@semantic-release/git",
      {
        assets: ["README.md", "pyproject.toml", "CHANGELOG.md"],
        message:
          "chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}",
        pushRepo: "https://github.com/djh00t/sops-pre-commit.git",
        push: false,
      },
    ],
    [
      "@semantic-release/exec",
      {
        publishCmd: `
          TWINE_USER_AGENT="$PYPI_USER_AGENT" poetry publish --build
        `,
      },
    ],
  ],
  preset: "conventionalcommits",
  releaseRules: [
    { type: "build", release: "patch" },
    { type: "chore", release: "patch" },
    { type: "ci", release: "patch" },
    { type: "docs", release: "patch" },
    { type: "feat", release: "minor" },
    { type: "fix", release: "patch" },
    { type: "perf", release: "patch" },
    { type: "refactor", release: "patch" },
    { type: "revert", release: "patch" },
    { type: "style", release: "patch" },
    { type: "test", release: "patch" },
    { type: "other", release: "patch" },
  ],
  parserOpts: {
    headerPattern:
      /^(?:[\u{1F300}-\u{1F6FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]\s)?(\w*)(?:\((.*)\))?!?:\s(.*)$/u,
    headerCorrespondence: ["type", "scope", "subject"],
    noteKeywords: ["BREAKING CHANGE", "BREAKING CHANGES"],
  },
  writerOpts: {
    transform: (commit, context) => {
      // Ensure the commit date is formatted correctly
      if (commit.committerDate) {
        commit.committerDate = new Date(commit.committerDate).toISOString();
      }

      // Transform commit types to human-friendly descriptions
      if (commit.type === 'feat') {
        commit.type = 'Features';
      } else if (commit.type === 'fix') {
        commit.type = 'Bug Fixes';
      } else if (commit.type === 'perf') {
        commit.type = 'Performance Improvements';
      } else if (commit.type === 'revert') {
        commit.type = 'Reverts';
      } else if (commit.type === 'docs') {
        commit.type = 'Documentation';
      } else {
        commit.type = 'Other Changes';
      }

      return commit;
    },
    commitsSort: ["subject", "scope"],
  },
};
