# Version Control with Git

Version control tracks changes to code over time, letting multiple people
work on the same codebase, revert mistakes, and understand the history of
why code changed. Git is the dominant version control system used across
backend (and virtually all) software development.

## Core concepts

- **Repository (repo)**: a project's full history of tracked changes.
- **Commit**: a saved snapshot of changes, with a message describing what
  changed and why.
- **Branch**: an independent line of development — typically used so a
  developer can work on a feature or fix without affecting the main
  codebase until it's ready.
- **Merge**: combining changes from one branch into another.
- **Clone**: copying a remote repository to a local machine.
- **Push / Pull**: sending local commits to a remote repository, or
  fetching and integrating commits from a remote repository.

## A typical workflow

```bash
git clone <repo-url>        # copy a repo locally
git checkout -b feature/x   # create and switch to a new branch
# ...make changes...
git add .                   # stage changes
git commit -m "Add feature x"
git push -u origin feature/x
# open a pull request for review, then merge into main
```

## Repo hosting services

Git itself is just the version-control tool; hosting the repository
remotely (so a team can collaborate) is done via a **repo hosting
service** — most commonly **GitHub** or **GitLab**. These add collaboration
features on top of raw Git: pull/merge requests (proposing and reviewing
changes before merging), issue tracking, and CI/CD pipeline integration
(see the CI/CD document).

## Why backend engineers need this

- **Collaboration**: multiple developers can work on the same backend
  codebase simultaneously without overwriting each other's work.
- **History and accountability**: `git blame` and commit history show who
  changed what and why, invaluable when debugging a regression.
- **Safety net**: bad changes can be reverted; branches let risky work
  happen in isolation from a stable `main` branch.
- **Enables CI/CD**: automated pipelines are typically triggered by Git
  pushes or pull requests (see the CI/CD Pipelines document).

## Free resources

- [Git — official documentation](https://git-scm.com/docs)
- [Pro Git book (free, official)](https://git-scm.com/book/en/v2)
- [GitHub Docs](https://docs.github.com/)
