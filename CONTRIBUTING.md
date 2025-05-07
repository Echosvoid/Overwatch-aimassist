# Contributing to Overwatch Aim Assist

Thank you for your interest in contributing to Overwatch Aim Assist! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

### 1. Fork the Repository

1. Go to [Overwatch Aim Assist](https://github.com/Echosvoid/Overwatch-aimassist)
2. Click the "Fork" button
3. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Overwatch-aimassist.git
   ```

### 2. Set Up Development Environment

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 4. Make Changes

1. Write your code
2. Add tests
3. Update documentation
4. Follow coding standards

### 5. Commit Changes

```bash
git add .
git commit -m "Description of changes"
```

### 6. Push Changes

```bash
git push origin feature/your-feature-name
```

### 7. Create Pull Request

1. Go to your fork on GitHub
2. Click "New Pull Request"
3. Select the main repository
4. Fill in the PR template

## Development Guidelines

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings
- Keep functions small and focused

### Testing

1. Write unit tests for new features
2. Ensure all tests pass:
   ```bash
   python -m pytest tests/
   ```
3. Maintain test coverage:
   ```bash
   python -m pytest --cov=src tests/
   ```

### Documentation

1. Update README.md if needed
2. Add docstrings to new functions
3. Update API documentation
4. Add comments for complex logic

### Git Workflow

1. Keep commits atomic
2. Write clear commit messages
3. Rebase on main before PR
4. Squash commits if needed

## Pull Request Process

1. Update documentation
2. Add tests
3. Ensure CI passes
4. Get code review
5. Address feedback
6. Merge when approved

## Issue Reporting

1. Use the issue template
2. Provide reproduction steps
3. Include system info
4. Add screenshots if needed

## Feature Requests

1. Check existing issues
2. Use the feature request template
3. Explain the use case
4. Suggest implementation

## Code Review

1. Be constructive
2. Focus on the code
3. Suggest improvements
4. Test the changes

## Release Process

1. Update version
2. Update changelog
3. Create release notes
4. Tag release
5. Deploy

## Getting Help

- Join our [Discord Server](https://discord.gg/overwatch-aimassist)
- Check the [Documentation](docs/README.md)
- Ask in issues

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License. 