.PHONY: help build start stop test clean repl logs

help:
	@echo "Makefile Commands"
	@echo "============================"
	@echo ""
	@echo "Quick Start:"
	@echo "  make start        - Build and start the application (Docker)"
	@echo "  make stop         - Stop the application"
	@echo ""
	@echo "Development:"
	@echo "  make test         - Run all tests"
	@echo "  make repl         - Start interactive REPL"
	@echo "  make logs         - View application logs"
	@echo ""
	@echo "Maintenance:"
	@echo "  make build        - Build Docker image"
	@echo "  make clean        - Remove containers and volumes"
	@echo "  make reset        - Full cleanup and rebuild"
	@echo ""

# Docker commands
build:
	@echo "🔨 Building Docker image..."
	docker-compose build

start:
	@echo "Starting the application..."
	@echo "Building and starting containers..."
	docker-compose up --build -d
	@echo ""
	@echo "Application started!"
	@echo "Open your browser to: http://localhost:8080"
	@echo ""
	@echo "View logs with: make logs"
	@echo "Stop with: make stop"

stop:
	@echo "Stopping application..."
	docker-compose down
	@echo "Application stopped"

logs:
	docker-compose logs -f

clean:
	@echo "🧹 Cleaning up containers and volumes..."
	docker-compose down -v
	@echo "Cleanup complete"

reset: clean build start
	@echo "Full reset complete!"

# Local development commands
test:
	@echo "🧪 Running tests..."
	@if [ -d "venv" ]; then \
		. venv/bin/activate && pytest tests/ -v; \
	else \
		echo "Virtual environment not found. Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"; \
	fi

repl:
	@echo "🔍 Starting PyRelDB REPL..."
	@if [ -d "venv" ]; then \
		. venv/bin/activate && python -m pyreldb.repl; \
	else \
		echo "Virtual environment not found. Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"; \
	fi

# Setup commands
setup:
	@echo "Setting up development environment..."
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	cd web-app && npm install
	@echo "Setup complete!"
	@echo "Run 'make test' to verify installation"

