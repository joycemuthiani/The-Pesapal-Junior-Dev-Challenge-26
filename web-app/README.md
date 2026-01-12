# Pesapal Payment Management System

> **Modern React + TypeScript web application for payment management, powered by a custom-built relational database management system.**

A full-featured single-page application (SPA) built with React 18 and TypeScript, providing a comprehensive payment management interface for processing customer transactions, managing merchants, and tracking payment data.

---

## ✨ Features

### 📊 Dashboard
- **Real-time Statistics**: Live database metrics and transaction analytics
- **Transaction Volume Analytics**: Filter by Day, Month, Year, or All with interactive date pickers
- **Status Breakdown**: Visual tree representation of transaction statuses (Completed, Pending, Failed)
- **Database Statistics**: Complete database information including all tables
- **Test Data Loader**: One-click test data generation (25 customers, 12 merchants, 70 transactions)
- **Modern UI**: Gradient cards, responsive design, professional aesthetics

### 👥 Customer Management
- **Full CRUD Operations**: Create, Read, Update, Delete customers
- **Advanced Search**: Real-time filtering by name, email, or phone
- **Pagination**: Efficient data display (10 items per page)
- **Balance Management**: Track customer account balances
- **Soft Delete**: Customers with transactions are hidden (not deleted) for data integrity
- **Confirmation Dialogs**: Type-to-confirm deletion for safety
- **Form Validation**: Client and server-side validation

### 🏪 Merchant Management
- **Business Account Management**: Create and manage merchant accounts
- **Category Filtering**: Filter by business category (Retail, Restaurant, Services, etc.)
- **Advanced Search**: Search by business name, email, or paybill number
- **Transaction Tracking**: Automatic total transaction amount calculation
- **Pagination**: Efficient data display

### 💰 Transaction Processing
- **JOIN Demonstrations**: Real-time INNER JOIN queries combining customers, merchants, and transactions
- **Status Management**: Track completed, pending, and failed transactions
- **Payment Methods**: Support for M-PESA, Card, Bank Transfer, Cash
- **Advanced Filtering**:
  - Filter by status (Completed, Pending, Failed)
  - Filter by payment method
  - Search by customer, merchant, or amount
- **Pagination**: Handle large transaction volumes efficiently
- **Metadata Tracking**: Date added, added by, and source information
- **Balance Validation**: Automatic balance checking before transaction creation
- **Real-time Updates**: Instant balance and merchant total updates

### 🔍 SQL Console
- **Interactive Query Interface**: Execute any SQL query directly
- **Formatted Results**: Beautiful table display of query results
- **Example Queries**: Pre-loaded examples for quick testing
- **Error Handling**: Clear error messages for invalid queries
- **Real-time Execution**: Instant query results

---

## 🛠️ Tech Stack

### Frontend
- **React 18**: Modern React with hooks
- **TypeScript**: Type-safe development
- **Modern CSS**: Custom styling with gradients, animations, and responsive design
- **Axios**: HTTP client for API communication

### Backend
- **Flask**: Python web framework
- **RESTful API**: JSON-based API design
- **CORS**: Cross-origin resource sharing enabled
- **Gunicorn**: Production WSGI server

### Database
- **Custom RDBMS**: Built-from-scratch relational database (see main README)
- **File-based Storage**: JSON persistence
- **B-tree Indexing**: Fast query performance

---

## 🚀 Quick Start

### Using Docker (Recommended)

The web application is automatically included when running the main project:

```bash
# From project root
docker-compose up --build

# Application available at http://localhost:8080
```

### Local Development

#### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Backend running (see main README)

#### Frontend Setup

```bash
# Install dependencies
npm install

# Start development server
npm start

# Application runs on http://localhost:3000
# (Proxies API requests to http://localhost:8080)
```

#### Production Build

```bash
# Build optimized production bundle
npm run build

# Output in build/ directory
```

---

## 📡 API Documentation

### Base URL
- **Development**: `http://localhost:8080/api`
- **Production**: Configure via `REACT_APP_API_URL` environment variable

### Endpoints

#### Health Check
```http
GET /api/health
```
Returns database status and health information.

**Response:**
```json
{
  "status": "ok",
  "database": "payment_system"
}
```

#### Customers

**List All Customers**
```http
GET /api/customers
```
Returns all active customers (soft-deleted customers are excluded).

**Response:**
```json
{
  "customers": [
    {
      "id": 1,
      "name": "Alice Mwangi",
      "email": "test1@test.com",
      "phone": "+254712345678",
      "balance": 5000.00,
      "is_active": true
    }
  ]
}
```

**Create Customer**
```http
POST /api/customers
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+254712345679",
  "balance": 1000.00
}
```

**Get Customer**
```http
GET /api/customers/:id
```

**Update Customer**
```http
PUT /api/customers/:id
Content-Type: application/json

{
  "name": "Jane Doe",
  "balance": 2000.00
}
```

**Delete Customer**
```http
DELETE /api/customers/:id
```
- If customer has transactions: Soft delete (sets `is_active = false`)
- If customer has no transactions: Hard delete (removes from database)

#### Merchants

**List All Merchants**
```http
GET /api/merchants
```

**Create Merchant**
```http
POST /api/merchants
Content-Type: application/json

{
  "business_name": "SuperMart",
  "category": "Retail",
  "mpesa_paybill": "123456",
  "email": "test1@merchant.com"
}
```

#### Transactions

**List All Transactions (with JOINs)**
```http
GET /api/transactions
```
Returns transactions with customer and merchant names via INNER JOIN.

**Response:**
```json
{
  "transactions": [
    {
      "id": 1,
      "customer_id": 1,
      "merchant_id": 1,
      "amount": 500.00,
      "payment_method": "M-PESA",
      "status": "completed",
      "date_added": "2024-01-12 10:30:00",
      "added_by": "Web User",
      "source": "Web App",
      "name": "Alice Mwangi",
      "business_name": "SuperMart Kenya"
    }
  ]
}
```

**Create Transaction**
```http
POST /api/transactions
Content-Type: application/json

{
  "customer_id": 1,
  "merchant_id": 1,
  "amount": 500.00,
  "payment_method": "M-PESA",
  "status": "completed"
}
```

**Validation:**
- Checks customer exists
- Checks merchant exists
- Validates sufficient customer balance
- Automatically updates customer balance
- Automatically updates merchant total_transactions

#### Statistics

**Get Database Statistics**
```http
GET /api/stats
```

**Response:**
```json
{
  "total_customers": 25,
  "total_merchants": 12,
  "total_transactions": 70,
  "total_amount": 42135.84,
  "status_breakdown": {
    "completed": { "count": 43, "amount": 42135.84 },
    "pending": { "count": 14, "amount": 12892.83 },
    "failed": { "count": 13, "amount": 11583.27 }
  },
  "db_stats": {
    "name": "payment_system",
    "num_tables": 3,
    "tables": {
      "customers": {
        "columns": 7,
        "rows": 25,
        "indexes": 2,
        "size_kb": 0.0
      }
    }
  }
}
```

**Get Transaction Volume (Filtered)**
```http
GET /api/stats/volume?period=day:2024-01-12
GET /api/stats/volume?period=month:2024-01
GET /api/stats/volume?period=year:2024
GET /api/stats/volume?period=all
```

#### Query Execution

**Execute Raw SQL**
```http
POST /api/query
Content-Type: application/json

{
  "query": "SELECT * FROM customers WHERE balance > 1000;"
}
```

**Response:**
```json
{
  "columns": ["id", "name", "email", "balance"],
  "rows": [...],
  "row_count": 10,
  "message": "Query executed successfully"
}
```

#### Test Data

**Load Test Data**
```http
POST /api/load-test-data
```
Loads comprehensive test data:
- 25 customers
- 12 merchants
- 70 transactions (with mixed statuses)

**Response:**
```json
{
  "message": "Test data loaded successfully",
  "customers": 25,
  "merchants": 12,
  "transactions": 70
}
```

---

## 📁 Project Structure

```
web-app/
├── backend/
│   ├── app.py              # Flask REST API server
│   └── __init__.py
├── src/
│   ├── App.tsx             # Main application component
│   ├── App.css             # Global styles
│   ├── index.tsx           # Application entry point
│   ├── types.ts            # TypeScript type definitions
│   ├── components/
│   │   ├── Dashboard.tsx   # Dashboard with statistics
│   │   ├── Dashboard.css
│   │   ├── Customers.tsx   # Customer management
│   │   ├── Merchants.tsx   # Merchant management
│   │   ├── Transactions.tsx # Transaction processing
│   │   ├── QueryConsole.tsx # SQL query interface
│   │   ├── QueryConsole.css
│   │   └── Common.css      # Shared component styles
│   └── services/
│       └── api.ts          # API client (Axios)
├── public/
│   ├── index.html          # HTML template
│   └── favicon.ico
├── package.json            # Node.js dependencies
├── tsconfig.json           # TypeScript configuration
└── README.md               # This file
```


## 🔧 Development

### Environment Variables

Create a `.env` file in `web-app/` directory:

```env
REACT_APP_API_URL=http://localhost:8080/api
```

### Available Scripts

```bash
# Start development server
npm start

# Build for production
npm run build

# Run tests (if configured)
npm test

# Type checking
npx tsc --noEmit
```

### Code Quality

- **TypeScript**: Full type safety
- **ESLint**: Code linting (React app defaults)
- **Prettier**: Code formatting (recommended)

---

## 🎯 Key Demonstrations

### 1. JOIN Operations
The Transactions view demonstrates INNER JOIN by combining:
- `transactions` table (main data)
- `customers` table (customer names)
- `merchants` table (merchant names)

**Example Query:**
```sql
SELECT transactions.id, customers.name, merchants.business_name, transactions.amount
FROM transactions
INNER JOIN customers ON transactions.customer_id = customers.id
INNER JOIN merchants ON transactions.merchant_id = merchants.id;
```

### 2. CRUD Operations
All entities (customers, merchants, transactions) support full CRUD:
- **Create**: Add new records via forms
- **Read**: View all records with filtering
- **Update**: Edit existing records
- **Delete**: Remove records (with safety checks)

### 3. Data Integrity
- **Soft Delete**: Customers with transactions are preserved
- **Balance Validation**: Prevents overdrafts
- **Constraint Enforcement**: Primary keys and unique constraints

### 4. Real-time Analytics
- **Transaction Volume**: Filtered by time period
- **Status Breakdown**: Visual representation of transaction statuses
- **Database Statistics**: Complete database information

---

## 📊 Loading Test Data

The application includes a built-in test data loader to quickly populate the database with sample data for testing and demonstration.

### How to Load Test Data

1. **Navigate to Dashboard**
   - Open the application at `http://localhost:8080`
   - Click on the "Dashboard" tab in the navigation

2. **Locate the Load Test Data Button**
   - If the database is empty, you'll see a "Load Test Data" button in the hero section
   - The button appears below the feature tags

3. **Click "Load Test Data"**
   - A confirmation dialog will appear
   - Click "OK" to proceed

4. **Wait for Loading**
   - The button will show "Loading Test Data..." while processing
   - This may take a few seconds (loading 70 transactions)

5. **Automatic Refresh**
   - After successful loading, the page will automatically refresh
   - You'll see a success message with the data counts

### What Gets Loaded

The test data includes:

- **25 Customers**
  - Names: Alice Mwangi, Bob Otieno, Carol Njeri, etc.
  - Emails: test1@test.com through test25@test.com
  - Phone numbers: Kenyan format (+254...)
  - Balances: Varied amounts (KES 2,800 - KES 7,200)

- **12 Merchants**
  - Business names: SuperMart Kenya, Java House, Naivas, Uber Kenya, etc.
  - Categories: Retail, Restaurant, Transportation, Services, Entertainment
  - Emails: test1@merchant.com through test12@merchant.com
  - M-PESA paybill numbers

- **70 Transactions**
  - **Status Distribution:**
    - 60% Completed (43 transactions)
    - 25% Pending (14 transactions)
    - 15% Failed (13 transactions)
  - **Date Range:** Last 30 days + today
  - **Payment Methods:** M-PESA, Card, Bank Transfer, Cash
  - **Amounts:** KES 50 - KES 2,000 (randomized)
  - **Metadata:** Date added, added by, source information

### After Loading

Once test data is loaded:

- ✅ Dashboard shows updated statistics
- ✅ Customers page displays 25 customers
- ✅ Merchants page displays 12 merchants
- ✅ Transactions page displays 70 transactions
- ✅ Transaction Volume card shows filtered analytics
- ✅ All filters and search features are ready to test

### Important Notes

- **One-Time Load**: Test data can only be loaded when the database is empty
- **No Duplicates**: If data already exists, you'll see an error message
- **Real Data**: All transactions are properly linked to customers and merchants
- **Balance Updates**: Customer balances and merchant totals are automatically calculated

---

## 🔍 Using the SQL Console

The SQL Console provides a powerful interface to execute any SQL query directly against the database, perfect for testing the custom RDBMS capabilities.

### Accessing the SQL Console

1. **Navigate to SQL Console**
   - Open the application at `http://localhost:8080`
   - Click on the "SQL Console" tab in the navigation bar

2. **Console Interface**
   - You'll see a text area for entering SQL queries
   - Example queries are provided below the input area
   - Results are displayed in a formatted table below

### Basic Usage

#### 1. Execute a Simple Query

```sql
SELECT * FROM customers;
```

- Type your query in the text area
- Click "Execute Query" button
- Results appear in a formatted table below

#### 2. Query with WHERE Clause

```sql
SELECT * FROM customers WHERE balance > 5000;
```

#### 3. Create a New Table

```sql
CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    price FLOAT,
    category VARCHAR(50)
);
```

After creating a table, it will appear in the Database Statistics section on the Dashboard!

#### 4. Insert Data

```sql
INSERT INTO products (id, name, price, category)
VALUES (1, 'Laptop', 50000, 'Electronics');
```

#### 5. JOIN Queries

```sql
SELECT
    customers.name,
    transactions.amount,
    merchants.business_name
FROM transactions
INNER JOIN customers ON transactions.customer_id = customers.id
INNER JOIN merchants ON transactions.merchant_id = merchants.id
WHERE transactions.amount > 1000;
```

### Example Queries

The SQL Console includes pre-loaded example queries you can click to try:

#### View All Tables
```sql
SELECT * FROM customers;
```

#### Filter Transactions
```sql
SELECT * FROM transactions WHERE status = 'completed';
```

#### Complex JOIN
```sql
SELECT
    customers.name AS customer,
    merchants.business_name AS merchant,
    transactions.amount,
    transactions.status
FROM transactions
INNER JOIN customers ON transactions.customer_id = customers.id
INNER JOIN merchants ON transactions.merchant_id = merchants.id
ORDER BY transactions.amount DESC;
```

#### Aggregate Queries
```sql
SELECT
    status,
    COUNT(*) as count,
    SUM(amount) as total
FROM transactions
GROUP BY status;
```

### Supported SQL Operations

The SQL Console supports all SQL operations implemented in the custom RDBMS:

- ✅ **CREATE TABLE**: Define new tables with columns and constraints
- ✅ **INSERT**: Add new rows to tables
- ✅ **SELECT**: Query data with WHERE, ORDER BY, LIMIT
- ✅ **UPDATE**: Modify existing rows
- ✅ **DELETE**: Remove rows
- ✅ **CREATE INDEX**: Create indexes for faster queries
- ✅ **DROP TABLE**: Remove tables
- ✅ **INNER JOIN**: Combine data from multiple tables
- ✅ **LEFT JOIN**: Include all rows from left table

### Data Types Supported

- **INT**: Integer numbers
- **VARCHAR(n)**: Variable-length strings
- **FLOAT**: Floating-point numbers
- **BOOLEAN**: True/False values
- **DATETIME**: Date and time values

### Constraints Supported

- **PRIMARY KEY**: Unique identifier
- **UNIQUE**: Unique values
- **NOT NULL**: Required field
- **DEFAULT**: Default value

### Tips for Using SQL Console

1. **Always End with Semicolon**: Queries must end with `;`
2. **Case Insensitive**: SQL keywords are case-insensitive
3. **String Quotes**: Use single quotes `'value'` for strings
4. **Table Names**: Use exact table names (customers, merchants, transactions)
5. **Error Messages**: Read error messages carefully - they help identify issues
6. **Results Format**: Results are displayed in a clean, formatted table
7. **Large Results**: For large result sets, use LIMIT to restrict rows

### Common Use Cases

#### Check Database State
```sql
SELECT COUNT(*) as total_customers FROM customers;
SELECT COUNT(*) as total_transactions FROM transactions;
```

#### Find High-Value Transactions
```sql
SELECT * FROM transactions
WHERE amount > 1000
ORDER BY amount DESC
LIMIT 10;
```

#### Customer Transaction Summary
```sql
SELECT
    customers.name,
    COUNT(transactions.id) as transaction_count,
    SUM(transactions.amount) as total_spent
FROM customers
LEFT JOIN transactions ON customers.id = transactions.customer_id
GROUP BY customers.id, customers.name;
```

#### Create Custom Tables
```sql
CREATE TABLE orders (
    id INT PRIMARY KEY,
    customer_id INT,
    product_name VARCHAR(100),
    quantity INT,
    order_date DATETIME
);

INSERT INTO orders (id, customer_id, product_name, quantity, order_date)
VALUES (1, 1, 'Laptop', 1, '2024-01-12 10:00:00');
```

### Error Handling

If a query fails, you'll see an error message explaining what went wrong:

- **Syntax Errors**: "Unexpected token..." or "Expected..."
- **Table Not Found**: "Table 'table_name' does not exist"
- **Column Errors**: "Column 'column_name' does not exist"
- **Constraint Violations**: "Duplicate value for PRIMARY KEY" or "UNIQUE constraint violation"

### Integration with Dashboard

Tables created in the SQL Console will automatically appear in:
- **Database Statistics** section on Dashboard
- **Table Names** list
- **Table Statistics** with row counts, columns, indexes

---

## 📝 Notes

### Architecture Decisions

1. **TypeScript**: Chosen for type safety and better developer experience
2. **Component-Based**: Modular React components for maintainability
3. **API-First**: Clear separation between frontend and backend
4. **State Management**: React hooks for local state management
5. **Error Handling**: Comprehensive error handling at API and UI levels

### Performance Considerations

- **Pagination**: Limits data transfer for large datasets
- **Client-Side Filtering**: Fast filtering without server round-trips
- **Optimized Builds**: Production builds are minified and optimized
- **Lazy Loading**: Components load on demand

### Security Features

- **Input Validation**: Both client and server-side validation
- **SQL Injection Prevention**: Parameterized queries via custom RDBMS
- **CORS Configuration**: Proper cross-origin setup
- **Error Sanitization**: Errors don't expose sensitive information

---


### Docker Deployment

The application is containerized in the main Docker setup:
- Frontend is built during Docker build
- Served statically by Flask
- Single container deployment
- Port 8080 (external) → 5000 (internal)




## 👤 Author

Built for **Pesapal Junior Developer Challenge '26**
