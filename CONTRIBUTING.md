# Git Workflow

The project uses the following Git workflow:

- **main**: Production code
- **development**: Development branch
- **feature/{number}-{name}**: Branches for developing new features
- **bugfix/{number}-{name}**: Branches for fixing bugs during development
- **hotfix/{number}-{name}**: Branches for fixing bugs in production
- **release/{version}**: Branches for final testing before production release

## Getting Started

## Forking the Repository

1. Go to the [Your Project Name] repository on GitHub.
2. Click the "Fork" button at the top right corner of the page.
3. This will create a copy of the repository in your GitHub account.

## Cloning Your Fork

1. Navigate to your forked repository on GitHub.
2. Click the "Code" button and copy the URL.
3. Open your terminal and run the following command:

```sh
git clone https://github.com/your-username/your-project-name.git
```

Navigate to the project directory.
```sh
cd your-project-name
```

Add the original repository as a remote called upstream.
```sh
git remote add upstream https://github.com/original-username/original-repo-name.git
```

Create development branch if not exists in your repoistory.
```sh
git checkout -b development
git pull upstream development
```

## Steps

1. **To add a new feature:**

    ```sh
    git checkout development
    git pull upstream development

    git checkout -b feature/{number}-{name}
    # Example:
    # git checkout -b feature/001-login-system
    # git checkout -b feature/002-workspace-system
    # Develop and commit your code
    git add .
    git commit -m "Description of the feature"
    git push origin feature/{number}-{name}
    # Example:
    git push origin feature/001-login-system
    git push origin feature/002-workspace-system

    create pull request
    ```

2. **To fix a bug during development:**

    ```sh
    git checkout development
    git pull upstream development

    git checkout -b bugfix/{number}-{name}
    # Example:
    # git checkout -b bugfix/001-fix-login-error
    # git checkout -b bugfix/002-correct-date-format
    # Fix the bug
    git add .
    git commit -m "Description of the bug fix"
    git push origin bugfix/{number}-{name}
    # Example:
    git push origin bugfix/001-login-error
    git push origin bugfix/002-correct-date-format

    create pull request
    ```

3. **To fix a bug in production:**

    ```sh
    git checkout main
    git pull upstream main

    git checkout -b hotfix/{number}-{name}
    # Example:
    # git checkout -b hotfix/001-login-crash
    # Fix the bug
    git add .
    git commit -m "Description of the bug fix"
    git push origin hotfix/{number}-{name}
    # Example:
    git push origin hotfix/001-login-crash

    create pull request
    ```

## Creating a Pull Request

1. Navigate to the original [Your Project Name] repository on GitHub.
2. Click the "Pull requests" tab, then the "New pull request" button.
3. Select your fork and branch as the source, and the original repository's development branch as the destination.
4. Provide a descriptive title and detailed description of your changes.
5. Click "Create pull request."

Congratulations! You've successfully created a pull request.

## Pull Request Guidelines

1. Branch: Ensure your pull request is aimed at the development branch, not the main branch.

2. Title: Use a clear and concise title that describes the changes. Follow the format:

3.  Feature: Add [Feature Name] or Implement [Feature Name]
    Bugfix: Fix [Bug Description]
    Hotfix: Fix [Critical Issue]
    Release: Prepare release [Version Number]

4. Description: Provide a detailed description of the changes, including:

What changes were made
Why the changes were necessary
Any relevant issues or bugs fixed (reference them with #issue-number)


## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
