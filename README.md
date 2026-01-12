### Pesapal Junior Developer Challenge '26 Submission


> A fully functional relational database management system (RDBMS) built from scratch in Python, featuring SQL parser, B-tree indexing, JOIN operations, and a payment management web application.

---

## Quick Start

### Using the Setup Script (Easiest Way)

The easiest way to get started is using the provided `run.sh` script:

```bash
# Clone the repository
git clone <your-repo-url>
cd pesapal-junior-dev-challenge

# Make the script executable (if needed)
chmod +x run.sh

# Run the setup script
./run.sh
```

The script will:
- ✅ Check if Docker and docker-compose are installed
- ✅ Build and start the application automatically
- ✅ Wait for the application to be ready
- ✅ Display helpful information (URLs, commands)

**What you'll see:**
- Dashboard: http://localhost:8080
- SQL Console: http://localhost:8080 (then click SQL Console tab)
- API Health: http://localhost:8080/api/health

**Useful commands:**
- View logs: `docker-compose logs -f`
- Stop app: `docker-compose down`

### Using Docker Directly (Alternative)

If you prefer to use Docker commands directly:

```bash
# Clone the repository
git clone <your-repo-url>
cd pesapal-junior-dev-challenge

# Start everything with one command
docker-compose up --build

# Open your browser to http://localhost:8080
```

That's it! The application is now running with:
- ✅ Backend API
- ✅ Frontend UI
- ✅ Database initialized with sample data
- ✅ All dependencies installed

**To stop:** Press `Ctrl+C` and run `docker-compose down`


## Features

### Core RDBMS Features
- ✅ **SQL Parser**: Full tokenization and syntax parsing
- ✅ **Data Types**: INT, VARCHAR, FLOAT, BOOLEAN, DATETIME
- ✅ **CRUD Operations**: CREATE, INSERT, SELECT, UPDATE, DELETE
- ✅ **B-Tree Indexing**: O(log n) search complexity
- ✅ **Constraints**: Primary keys, unique constraints, NOT NULL
- ✅ **JOIN Operations**: INNER JOIN and LEFT JOIN
- ✅ **Query Optimization**: Index-aware execution
- ✅ **Persistence**: File-based storage with atomic writes
- ✅ **Interactive REPL**: Command-line database interface

### Web Application
- **Payment Management**
- **Customer Management**: Full CRUD operations
- **Merchant Management**: Business account tracking
- **Transaction Processing**: Real-time payment records with JOINs
- **SQL Console**: Interactive query interface
- **Dashboard**: System statistics and metrics

---

## Testing Guide for Reviewers

### Option 1: Using the Setup Script (Easiest - Recommended)

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd pesapal-junior-dev-challenge

# 2. Make the script executable (if needed)
chmod +x run.sh

# 3. Run the setup script (automatically builds and starts everything)
./run.sh

# 4. Open browser to http://localhost:8080

# 5. Test the application:
#    - View Dashboard (see database stats)
#    - Go to Customers tab → Add/Edit/Delete customers
#    - Go to Merchants tab → Add merchants
#    - Go to Transactions tab → Create transactions (see JOINs in action!)
#    - Go to SQL Console → Run custom queries

# 6. Stop the application
docker-compose down
```

The `run.sh` script automatically:
- Checks for Docker installation
- Builds and starts the application
- Waits for the app to be ready
- Displays helpful URLs and commands

### Option 2: Docker Commands Directly

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd pesapal-junior-dev-challenge

# 2. Start with Docker (builds and runs everything)
docker-compose up --build

# 3. Open browser to http://localhost:8080

# 4. Test the application:
#    - View Dashboard (see database stats)
#    - Go to Customers tab → Add/Edit/Delete customers
#    - Go to Merchants tab → Add merchants
#    - Go to Transactions tab → Create transactions (see JOINs in action!)
#    - Go to SQL Console → Run custom queries

# 5. Stop the application
# Press Ctrl+C, then:
docker-compose down
```

### Option 3: Test the REPL (Command-Line Interface)

```bash
# 1. Install Python dependencies
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Run the interactive REPL
python -m pyreldb.repl
```

**Run these commands in the REPL:**

```sql
-- Create a table
CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price FLOAT,
    category VARCHAR(50)
);

-- Insert data
INSERT INTO products (id, name, price, category) VALUES (1, 'Laptop', 50000, 'Electronics');
INSERT INTO products (id, name, price, category) VALUES (2, 'Phone', 30000, 'Electronics');
INSERT INTO products (id, name, price, category) VALUES (3, 'Desk', 15000, 'Furniture');

-- Query with WHERE
SELECT * FROM products WHERE price > 20000;

-- Update
UPDATE products SET price = 45000 WHERE id = 1;

-- Create another table for JOINs
CREATE TABLE orders (
    id INT PRIMARY KEY,
    product_id INT,
    quantity INT,
    customer_name VARCHAR(100)
);

INSERT INTO orders (id, product_id, quantity, customer_name) VALUES (1, 1, 2, 'Alice');
INSERT INTO orders (id, product_id, quantity, customer_name) VALUES (2, 2, 1, 'Bob');

-- JOIN query
SELECT
    products.name,
    products.price,
    orders.quantity,
    orders.customer_name
FROM orders
INNER JOIN products ON orders.product_id = products.id;

-- Show all tables
.tables

-- Show table schema
.schema products

-- Show database stats
.stats

-- Exit
.exit
```

### Option 4: Run Tests

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=pyreldb tests/

# Expected output: 30+ tests passing
```



## Manual set up(not preferred)

Preferred when there is need to change something in the code

### Prerequisites
- Python 3.11 or higher
- Node.js 18+ and npm
- Docker (optional, for containerized deployment)

### Backend Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend
python -m web-app.backend.app
```

Backend will be available at `http://localhost:5000`

### Frontend Setup

```bash
# Install dependencies
cd web-app
npm install

# Run development server
npm start
```

Frontend will be available at `http://localhost:3000`

### REPL Usage

```bash
# Activate virtual environment
source venv/bin/activate

# Run REPL
python -m pyreldb.repl

# Use .help for available commands
```

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
├──────────────────────┬──────────────────────────────────────┤
│   REPL Interface     │   Web App (React + Flask)            │
└──────────────────────┴──────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Query Executor                            │
│  • Query planning  • WHERE evaluation  • JOIN algorithms     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      SQL Parser                              │
│  • Tokenization  • Syntax parsing  • AST generation          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Table Management                          │
│  • Schema  • Rows  • Constraints  • Validation               │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
          ┌──────────────────┐  ┌─────────────────┐
          │  B-Tree Indexing │  │ Storage Engine  │
          │  • O(log n)      │  │ • JSON persist  │
          │  • Range queries │  │ • Atomic writes │
          └──────────────────┘  └─────────────────┘
```

### Component Details

#### 1. SQL Parser (`pyreldb/parser.py`)
- **Tokenizer**: Lexical analysis, handles keywords, identifiers, strings, numbers
- **Parser**: Recursive descent parser producing Abstract Syntax Tree (AST)
- **Supported SQL**: CREATE TABLE, INSERT, SELECT (with WHERE, JOIN, ORDER BY, LIMIT), UPDATE, DELETE

#### 2. Storage Engine (`pyreldb/storage.py`)
- **Format**: JSON (human-readable, easy to debug)
- **Atomicity**: Write to temp file, then atomic rename
- **Auto-save**: Persists after every modification

#### 3. B-Tree Indexing (`pyreldb/index.py`)
- **Algorithm**: Classic B-tree with configurable order
- **Complexity**: O(log n) for search, insert, delete
- **Features**: Range queries, automatic index creation for primary/unique keys

#### 4. Query Executor (`pyreldb/executor.py`)
- **Optimization**: Uses indexes when available
- **JOINs**: Nested loop join algorithm (INNER and LEFT JOIN)
- **Filtering**: Efficient WHERE clause evaluation

#### 5. Table Management (`pyreldb/table.py`)
- **Schema**: Column definitions with types and constraints
- **Constraints**: Primary key, unique, NOT NULL enforcement
- **Validation**: Type checking and conversion

---

## Main Project Structure

```
pesapal-junior-dev-challenge/
├── Dockerfile                 # Docker build configuration
├── docker-compose.yml         # One-command deployment
├── requirements.txt           # Python dependencies
├── pytest.ini                 # Test configuration
│
├── pyreldb/                   # Core RDBMS implementation
│   ├── __init__.py
│   ├── types.py              # Data types (INT, VARCHAR, FLOAT, etc.)
│   ├── table.py              # Table and row management
│   ├── index.py              # B-tree indexing
│   ├── parser.py             # SQL parser (tokenizer + parser)
│   ├── executor.py           # Query execution engine
│   ├── storage.py            # Persistence (save/load)
│   └── repl.py               # Interactive REPL interface
│
├── web-app/                  # Demo web application
│   ├── backend/
│   │   ├── __init__.py
│   │   └── app.py           # Flask REST API
│   ├── src/                 # React frontend
│   │   ├── App.js
│   │   ├── components/
│   │   │   ├── Dashboard.js
│   │   │   ├── Customers.js
│   │   │   ├── Merchants.js
│   │   │   ├── Transactions.js
│   │   │   └── QueryConsole.js
│   │   └── services/
│   │       └── api.js
│   ├── public/
│   └── package.json
│
├── tests/                    # Comprehensive test suite
│   ├── test_types.py        # Data type tests
│   ├── test_table.py        # Table operation tests
│   ├── test_parser.py       # SQL parser tests
│   └── test_integration.py  # End-to-end tests
│
└── data/                     # Database files (runtime)
```

---

## API Documentation

### Base URL
- Development: `http://localhost:5000/api`
- Docker: `http://localhost:5000/api`

### Endpoints

#### Health Check
```
GET /api/health
Response: {"status": "ok", "database": "payment_system"}
```

#### Customers
```
GET    /api/customers           # List all customers
POST   /api/customers           # Create customer
GET    /api/customers/:id       # Get customer by ID
PUT    /api/customers/:id       # Update customer
DELETE /api/customers/:id       # Delete customer
```

#### Merchants
```
GET    /api/merchants           # List all merchants
POST   /api/merchants           # Create merchant
```

#### Transactions
```
GET    /api/transactions        # List transactions (with JOINs)
POST   /api/transactions        # Create transaction
```

#### Raw SQL Query
```
POST   /api/query
Body:  {"query": "SELECT * FROM customers;"}
Response: {"columns": [...], "rows": [...], "row_count": n}
```

#### Statistics
```
GET    /api/stats
Response: Database statistics including table counts, row counts, index info
```

---

## SQL Exampsamplesles

### Creating Tables

```sql
-- Customers table
CREATE TABLE customers (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    balance FLOAT DEFAULT 0.0,
    created_at DATETIME
);

-- Merchants table
CREATE TABLE merchants (
    id INT PRIMARY KEY,
    business_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    mpesa_paybill VARCHAR(20),
    total_transactions FLOAT
);

-- Transactions table
CREATE TABLE transactions (
    id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    merchant_id INT NOT NULL,
    amount FLOAT NOT NULL,
    payment_method VARCHAR(50),
    status VARCHAR(20)
);
```

### CRUD Operations

```sql
-- INSERT
INSERT INTO customers (id, name, email, balance)
VALUES (1, 'Alice Mwangi', 'alice@example.com', 5000.00);

-- SELECT with WHERE
SELECT * FROM customers WHERE balance > 1000;

-- UPDATE
UPDATE customers SET balance = 6000.00 WHERE id = 1;

-- DELETE
DELETE FROM customers WHERE id = 1;
```

### JOIN Queries

```sql
-- INNER JOIN: Get transactions with customer and merchant names
SELECT
    customers.name AS customer_name,
    merchants.business_name,
    transactions.amount,
    transactions.status
FROM transactions
INNER JOIN customers ON transactions.customer_id = customers.id
INNER JOIN merchants ON transactions.merchant_id = merchants.id
WHERE transactions.amount > 500;

-- LEFT JOIN: Get all customers and their transactions (if any)
SELECT
    customers.name,
    customers.balance,
    transactions.amount
FROM customers
LEFT JOIN transactions ON customers.id = transactions.customer_id;
```

### More Complex Queries

```sql
-- ORDER BY
SELECT * FROM customers ORDER BY balance DESC;

-- LIMIT
SELECT * FROM customers LIMIT 5;

-- Complex WHERE with AND/OR
SELECT * FROM customers
WHERE balance > 1000 AND (email LIKE '%gmail%' OR email LIKE '%yahoo%');

-- Create Index
CREATE INDEX idx_customer_email ON customers (email);
```




## Testing

### Run Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest --cov=pyreldb tests/

# Specific test file
pytest tests/test_parser.py -v
```

### Test Coverage

- **Unit Tests**: Individual components (types, parser, table, indexing)
- **Integration Tests**: End-to-end workflows (CRUD, JOINs, persistence)

---

## Docker Commands

```bash
# Build and start
docker-compose up --build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Remove volumes (reset database)
docker-compose down -v

# Rebuild from scratch
docker-compose down -v && docker-compose up --build
```

---


## 👤 Joyce Muthiani

**Joyce Muthiani**
- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com




[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
# The-Pesapal-Junior-Dev-Challenge-26
