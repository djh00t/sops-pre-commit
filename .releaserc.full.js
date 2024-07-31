// .releaserc.full.js
module.exports = {
    branches: ['main'],
    plugins: [
      '@semantic-release/commit-analyzer',
      '@semantic-release/release-notes-generator',
      '@semantic-release/changelog',
      [
        '@semantic-release/git',
        {
          assets: ['CHANGELOG.md', 'package.json', 'package-lock.json'],
          message: 'chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}',
        },
      ],
      [
        '@semantic-release/github',
        {
          successComment: false,
          failComment: false,
          labels: false,
          releasedLabels: false,
          addReleases: 'top',
        },
      ],
    ],
  };