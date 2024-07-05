module.exports = {
  branches: [
    `${process.env.RELEASE_BRANCH || 'release'}`
  ],
  plugins: [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    "@semantic-release/changelog",
    [
      "@semantic-release/exec",
      {
        "prepareCmd": "python setup.py sdist bdist_wheel"
      }
    ],
    [
      "@semantic-release/git",
      {
        "assets": [
          "CHANGELOG.md",
          "setup.py",
          "version.py"
        ],
        "message": "chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}",
        "branch": `release-${process.env.EPOCH_TIME || 'default'}`
      }
    ],
    [
      "@semantic-release/exec",
      {
        "prepareCmd": "git add CHANGELOG.md setup.py version.py && git commit -m 'chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}' && git push origin release-${process.env.EPOCH_TIME || 'default'}"
      }
    ],
    [
      "@semantic-release/github",
      {
        "successComment": false,
        "failComment": false,
        "addReleases": "bottom",
        "createRelease": true,
        "assets": "dist/*"
      }
    ],
    [
      "@semantic-release/exec",
      {
        "publishCmd": "gh pr create --title 'chore(release): ${nextRelease.version}' --body 'This PR includes the release ${nextRelease.version}.\n\n${nextRelease.notes}' --base main --head release-${process.env.EPOCH_TIME || 'default'}"
      }
    ]
  ]
};
