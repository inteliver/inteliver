---
title: "Git Flow"
---

# Simple Git Flow for New Features
Here's the git flow and branches guideline for inteliver developers and maintainers.

### Main Branches
- `main`: Stable, production-ready code.
- `develop`: Latest development version, contains all merged features.

### Feature Branches
Create a new branch for each feature or bug fix from the `develop` branch.

#### Naming Convention:
`feature/short-description`

Example: `feature/url-image-processing`

### Steps for Creating a New Feature Branch
1. Switch to develop:

```bash
git checkout develop
```

2. Pull the latest changes:

```bash
git pull origin develop
```

3. Create a new feature branch:

```bash
git checkout -b feature/your-feature-name
```

4. Work on the feature, committing changes frequently:

```bash
git add .
git commit -m "Short description of changes"
```

5. Push the feature branch to the remote repository:
```bash
git push origin feature/your-feature-name
```

6. Create a Pull Request to merge into `develop`:

Once the feature is complete, open a Pull Request (PR) to merge into `develop`.

7. Ensure all tests pass, and reviewers approve the changes.

Merge the PR into `develop` using Squash and Merge to keep the commit history clean.

8. Delete the feature branch locally and remotely:
```bash
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```


### External Contributions (Forking Workflow)
For external contributors, follow this workflow:

1. Fork the repository:
Click **"Fork"** on the repository page to create your copy of the project in your GitHub account.

2. Clone your fork:

```bash
git clone https://github.com/your-username/inteliver.git
cd inteliver
```

3. Create a feature branch based on the main branch of your fork:

```bash
git checkout -b feature/your-feature-name
```

4. Work on your changes, then commit them:

```bash
git add .
git commit -m "Short description of changes"
```

5. Keep your fork up to date with the upstream main branch:

```bash
git remote add upstream https://github.com/inteliver/inteliver.git
git fetch upstream
git checkout main
git pull upstream main
git checkout feature/your-feature-name
git rebase main
```

6. Push your changes to your fork:

```bash
git push origin feature/your-feature-name
```

7. Open a Pull Request from your fork's `feature/your-feature-name` branch to the `develop` branch of the original repository.

