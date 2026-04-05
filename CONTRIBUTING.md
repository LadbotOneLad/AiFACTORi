# Contributing to E14 Oracle

Thank you for your interest in contributing to the E14 Oracle project! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Welcome diverse perspectives
- Focus on constructive feedback
- Report violations privately

## How to Contribute

### Reporting Bugs

1. **Check existing issues** — avoid duplicates
2. **Create detailed report**:
   ```
   Title: [BUG] Brief description
   
   Expected behavior: ...
   Actual behavior: ...
   Steps to reproduce: ...
   Environment: OS, Python version, Docker version
   ```
3. **Provide reproducible example** — code, logs, stack trace

### Suggesting Features

1. **Check discussions** — see if already proposed
2. **Create feature request**:
   ```
   Title: [FEATURE] Brief description
   
   Use case: Why is this needed?
   Proposed solution: How should it work?
   Alternatives: Other approaches considered
   ```
3. **Wait for feedback** — maintainers will discuss feasibility

### Code Contributions

#### Setup Development Environment

```bash
# 1. Fork repository on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/AiFACTORi.git
cd AiFACTORi

# 3. Create feature branch
git checkout -b feature/your-feature-name

# 4. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 5. Install dev dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 6. Install pre-commit hooks
pre-commit install
```

#### Coding Standards

**Python (PEP 8)**
```python
# Use type hints
def compute_k_score(state: PhaseState, target: float = 0.0) -> float:
    """
    Compute ring coherence K-value.
    
    Args:
        state: 14 engines × 4 axes phase configuration
        target: Invariant target phase (default: 0.0)
    
    Returns:
        K-value (0.0 to 1.0), where 1.0 = perfect convergence
    
    Raises:
        ValueError: If state is malformed
    """
    # Implementation here
    pass

# Docstrings: Google style
# Max line length: 100 characters
# Indentation: 4 spaces
# Naming: snake_case for functions/variables, PascalCase for classes
```

**Testing**
```python
# Location: tests/test_*.py
# Use pytest
import pytest
from oracle_layer import E14Oracle

def test_convergence_detection():
    """Test oracle detects convergence at K=1.0."""
    oracle = E14Oracle()
    state = {
        f"E{i:02d}": {axis: 0.0 for axis in ["tick", "beat", "breath", "cycle"]}
        for i in range(1, 15)
    }
    assert oracle.convergence_now(state) == True

def test_scattered_state_not_converged():
    """Test oracle detects divergence at scattered phases."""
    oracle = E14Oracle()
    state = {
        f"E{i:02d}": {axis: float((i * 12345) % 86400) for axis in ["tick", "beat", "breath", "cycle"]}
        for i in range(1, 15)
    }
    assert oracle.convergence_now(state) == False
```

#### Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`

**Examples**:
```
feat(oracle): add branching futures evaluation

Implement Dr. Strange oracle capability to evaluate multiple decision paths
and select optimal convergence strategy.

Closes #42
```

```
fix(docker): resolve health check timeout in e14_live service

Health check was timing out due to missing psutil import. Added explicit
test for module availability.

Fixes #38
```

```
docs: update ARCHITECTURE.md with 6-axis model diagram

Added ASCII diagram showing temporal, thermal, and environmental axes.
```

#### Pull Request Process

1. **Create descriptive PR**:
   ```
   Title: [FEATURE/FIX] Brief description
   
   ## Description
   What does this PR accomplish?
   
   ## Related Issues
   Closes #42
   
   ## Testing
   - [ ] Added unit tests
   - [ ] Manual testing completed
   - [ ] All tests pass
   
   ## Checklist
   - [ ] Code follows PEP 8
   - [ ] Docstrings added
   - [ ] No breaking changes
   - [ ] Documentation updated
   ```

2. **Ensure CI passes**:
   - Tests pass: `pytest tests/`
   - Linting passes: `pylint src/`
   - Type checking: `mypy src/`

3. **Address review feedback** — be responsive and collaborative

4. **Squash commits** before merge (if requested)

### Documentation Contributions

1. **Update relevant docs** in `docs/` folder
2. **Use Markdown** with clear structure
3. **Add examples** where applicable
4. **Link to related docs** — help users navigate
5. **Proofread** — check grammar, spelling, clarity

**Example structure**:
```markdown
# Feature Name

## Overview
High-level explanation.

## How It Works
Detailed mechanism.

## Examples
Code examples showing usage.

## Configuration
Config options, environment variables.

## Troubleshooting
Common issues and solutions.

## See Also
Links to related docs.
```

### Translation Contributions

Currently English-only. Future: community translations welcome!

## Development Workflow

### Local Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_oracle.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run type checking
mypy src/

# Run linting
pylint src/

# Format code
black src/
```

### Docker Development

```bash
# Build image locally
docker build -t e14-oracle:dev .

# Test in container
docker run -it e14-oracle:dev python oracle_layer.py

# Test compose stack
docker-compose up -d
docker-compose logs -f e14_oracle
docker-compose down
```

### Git Workflow

```bash
# 1. Create feature branch from main
git checkout main
git pull origin main
git checkout -b feature/your-feature

# 2. Make commits (atomic, well-messaged)
git add file1.py file2.py
git commit -m "feat(scope): description"

# 3. Keep branch up-to-date
git fetch origin
git rebase origin/main

# 4. Push to your fork
git push origin feature/your-feature

# 5. Create PR on GitHub (wait for review)

# 6. After merge, clean up
git checkout main
git pull origin main
git branch -d feature/your-feature
```

## Release Process

(For maintainers)

```bash
# 1. Update version
# - src/__version__.py
# - setup.py
# - docs/CHANGELOG.md

# 2. Create release branch
git checkout -b release/1.1.0

# 3. Update CHANGELOG
# 4. Commit and push

# 5. Create pull request
# 6. Merge to main

# 7. Tag release
git tag -a v1.1.0 -m "Release 1.1.0"
git push origin v1.1.0

# 8. GitHub Actions builds and publishes
# 9. Announce on discussions
```

## Style Guide

### Python

- **Linter**: `pylint` (config in `.pylintrc`)
- **Formatter**: `black` (100 char line length)
- **Type checking**: `mypy` (strict mode)
- **Docstrings**: Google style
- **Imports**: Organized per `isort`

### Markdown

- **Max line length**: 100 characters
- **Headers**: Use `#` (not underlines)
- **Code blocks**: Specify language
- **Links**: Use reference-style for repeated links

### Docker

- **Base image**: `python:3.11-slim` (security, size)
- **Non-root user**: Always use non-root
- **Multi-stage**: Build optimization
- **Health checks**: All services

### Git Commits

- **One feature per commit** — atomic
- **Descriptive messages** — explain WHY
- **Reference issues** — `Closes #123`
- **No merge commits** — rebase before push

## Resources

- **Python**: https://pep8.org/, https://google.github.io/styleguide/pyguide.html
- **Git**: https://git-scm.com/book/en/v2
- **Docker**: https://docs.docker.com/develop/dev-best-practices/
- **Conventional Commits**: https://www.conventionalcommits.org/
- **Markdown**: https://www.markdownguide.org/

## Getting Help

- **Questions**: Create GitHub Discussion
- **Issues**: Search existing, then create new
- **Documentation**: Check `docs/` folder
- **Examples**: See `examples/` folder

## Recognition

We appreciate all contributions! Contributors will be:
- Added to `CONTRIBUTORS.md`
- Acknowledged in release notes
- Featured in project discussions

## Questions?

- Open a [GitHub Discussion](https://github.com/LadbotOneLad/AiFACTORi/discussions)
- Check [documentation](docs/)
- Review existing [pull requests](https://github.com/LadbotOneLad/AiFACTORi/pulls)

---

**Thank you for contributing to E14 Oracle! 🙏**
