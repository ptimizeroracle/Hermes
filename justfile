# Hermes - LLM Dataset Engine
# Justfile for common development tasks

# Default recipe to display help
default:
    @just --list

# Set up the development environment
setup:
    @echo "🔧 Setting up development environment..."
    uv sync
    @echo "✅ Environment ready!"

# Run all tests (unit + integration)
test:
    @echo "🧪 Running all tests..."
    uv run pytest -v

# Run only unit tests
test-unit:
    @echo "🧪 Running unit tests..."
    uv run pytest tests/unit/ -v

# Run only integration tests (requires GROQ_API_KEY)
test-integration:
    @echo "🧪 Running integration tests..."
    @if [ -z "$GROQ_API_KEY" ]; then \
        echo "⚠️  GROQ_API_KEY not set. Loading from .env..."; \
        export $(cat .env | xargs) && uv run pytest tests/integration/ -v; \
    else \
        uv run pytest tests/integration/ -v; \
    fi

# Run tests with coverage report
test-coverage:
    @echo "📊 Running tests with coverage..."
    uv run pytest --cov=hermes --cov-report=html --cov-report=term

# Run specific test file or test
test-file FILE:
    @echo "🧪 Running test: {{FILE}}"
    uv run pytest {{FILE}} -v

# Run tests with detailed output
test-verbose:
    @echo "🧪 Running tests with verbose output..."
    uv run pytest -vvs

# Run quick tests (fail fast)
test-quick:
    @echo "⚡ Running quick test (fail fast)..."
    uv run pytest -x -v

# Lint the codebase
lint:
    @echo "🔍 Linting code..."
    uv run ruff check hermes/
    uv run ruff check tests/

# Format the code
format:
    @echo "✨ Formatting code..."
    uv run ruff format hermes/
    uv run ruff format tests/

# Type check with mypy
typecheck:
    @echo "🔎 Type checking..."
    uv run mypy hermes/

# Run all quality checks (lint + format check + typecheck)
check: lint typecheck
    @echo "✅ All quality checks passed!"

# Clean build artifacts and cache
clean:
    @echo "🧹 Cleaning up..."
    rm -rf build/
    rm -rf dist/
    rm -rf *.egg-info
    rm -rf .pytest_cache/
    rm -rf .coverage
    rm -rf htmlcov/
    rm -rf .mypy_cache/
    rm -rf .ruff_cache/
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    @echo "✅ Cleanup complete!"

# Build the package
build: clean
    @echo "📦 Building package..."
    uv build

# Install the package locally
install:
    @echo "📦 Installing package..."
    uv pip install -e .

# Run CLI help
cli-help:
    @echo "📖 Hermes CLI Help"
    uv run hermes --help

# Inspect a data file
cli-inspect FILE:
    @echo "🔍 Inspecting {{FILE}}..."
    uv run hermes inspect -i {{FILE}}

# Validate a config file
cli-validate CONFIG:
    @echo "✅ Validating {{CONFIG}}..."
    uv run hermes validate --config {{CONFIG}}

# Process data with config
cli-process CONFIG:
    @echo "⚙️  Processing with {{CONFIG}}..."
    @export $(cat .env | xargs) && uv run hermes process --config {{CONFIG}}

# Estimate cost for a config
cli-estimate CONFIG:
    @echo "💰 Estimating cost for {{CONFIG}}..."
    @export $(cat .env | xargs) && uv run hermes estimate --config {{CONFIG}}

# Run a simple example
example NAME:
    @echo "🚀 Running example: {{NAME}}"
    @export $(cat .env | xargs) && uv run python examples/{{NAME}}.py

# Run quickstart example
quickstart:
    @just example 01_quickstart

# Run Groq example
groq-example:
    @just example 05_groq_example

# Start interactive Python shell with hermes loaded
shell:
    @echo "🐍 Starting Python shell..."
    @export $(cat .env | xargs) && uv run python -c "import hermes; from hermes import PipelineBuilder; print('Hermes loaded! Use PipelineBuilder to get started.'); import IPython; IPython.embed()"

# Generate documentation
docs:
    @echo "📚 Generating documentation..."
    @echo "TODO: Add sphinx or mkdocs setup"

# Run end-to-end test with real API
e2e-test:
    @echo "🌐 Running end-to-end test with Groq API..."
    @export $(cat .env | xargs) && uv run pytest tests/integration/test_end_to_end.py::TestEndToEndGroq -v

# Check test coverage percentage
coverage-report:
    @echo "📊 Coverage Report:"
    uv run pytest --cov=hermes --cov-report=term-missing --quiet
    @echo ""
    @echo "📁 Detailed HTML report: htmlcov/index.html"
    uv run pytest --cov=hermes --cov-report=html --quiet

# Open coverage report in browser
coverage-open: coverage-report
    @echo "🌐 Opening coverage report..."
    @command -v open >/dev/null && open htmlcov/index.html || xdg-open htmlcov/index.html || echo "Please open htmlcov/index.html manually"

# Watch tests (requires pytest-watch)
watch:
    @echo "👀 Watching for changes..."
    uv run ptw -- -v

# Create a new release (bump version and tag)
release VERSION:
    @echo "🚀 Creating release {{VERSION}}..."
    @echo "{{VERSION}}" > VERSION
    git add VERSION
    git commit -m "Release {{VERSION}}"
    git tag -a v{{VERSION}} -m "Version {{VERSION}}"
    @echo "✅ Release {{VERSION}} created!"
    @echo "📌 Push with: git push && git push --tags"

# Show project stats
stats:
    @echo "📊 Project Statistics"
    @echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    @echo "📁 Total Python files:"
    @find hermes -name "*.py" | wc -l
    @echo "📝 Lines of code (hermes/):"
    @find hermes -name "*.py" -exec wc -l {} + | tail -1 | awk '{print $1}'
    @echo "🧪 Test files:"
    @find tests -name "*.py" | wc -l
    @echo "📝 Lines of test code:"
    @find tests -name "*.py" -exec wc -l {} + | tail -1 | awk '{print $1}'
    @echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Run security check
security:
    @echo "🔒 Running security checks..."
    uv run pip-audit

# Update dependencies
update-deps:
    @echo "📦 Updating dependencies..."
    uv lock --upgrade

# Create test data and config files
create-test-files:
    @echo "📝 Creating test files..."
    @echo "question\nWhat is 2+2?\nWhat is the capital of France?\nWhat color is the sky?" > test_data.csv
    @echo "✅ Created test_data.csv"

# Run pre-commit checks (before committing)
pre-commit: format lint typecheck test-quick
    @echo "✅ Pre-commit checks passed!"

# Benchmark performance
benchmark:
    @echo "⚡ Running performance benchmarks..."
    @echo "TODO: Add benchmark suite"

# Check for outdated dependencies
check-deps:
    @echo "📦 Checking for outdated dependencies..."
    uv pip list --outdated

# Run integration tests with specific provider
test-provider PROVIDER:
    @echo "🧪 Testing {{PROVIDER}} integration..."
    @export $(cat .env | xargs) && uv run pytest tests/integration/test_{{PROVIDER}}_integration.py -v

# Cleanup test outputs
clean-test-outputs:
    @echo "🧹 Cleaning test outputs..."
    rm -f test_*.csv test_*.xlsx test_output.* 
    rm -rf .checkpoints/
    @echo "✅ Test outputs cleaned!"

# Full CI pipeline (what runs in CI/CD)
ci: clean setup lint typecheck test coverage-report
    @echo "✅ CI pipeline complete!"

# Development mode - run tests on file change
dev:
    @echo "👨‍💻 Development mode - watching for changes..."
    @echo "Press Ctrl+C to stop"
    uv run pytest-watch -- tests/ -v

# Run all examples
run-examples:
    @echo "🚀 Running all examples..."
    @for example in examples/*.py; do \
        echo "Running $$example..."; \
        export $(cat .env | xargs) && uv run python $$example || true; \
    done

# Initialize .env file if it doesn't exist
init-env:
    @if [ ! -f .env ]; then \
        echo "📝 Creating .env file..."; \
        echo "GROQ_API_KEY=your_api_key_here" > .env; \
        echo "OPENAI_API_KEY=your_api_key_here" >> .env; \
        echo "✅ .env file created! Please update with your API keys."; \
    else \
        echo "✅ .env file already exists"; \
    fi

# Show environment info
env-info:
    @echo "🔧 Environment Information"
    @echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    @echo "Python version:"
    @uv run python --version
    @echo ""
    @echo "Installed packages:"
    @uv pip list
    @echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

