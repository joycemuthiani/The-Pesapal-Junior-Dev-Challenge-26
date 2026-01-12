"""
Flask backend for payment management 
"""

import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Add parent directory to path to import pyreldb
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from pyreldb.storage import Database
from pyreldb.executor import QueryExecutor


app = Flask(__name__, static_folder='../build', static_url_path='')
CORS(app)  # Enable CORS for React frontend

# Initialize database
db = Database("payment_system", data_dir="data")
executor = QueryExecutor(db)


def init_demo_database():
    """Initialize demo database with sample schema"""
    try:
        # Create tables if they don't exist
        if not db.table_exists('customers'):
            executor.execute("""
                CREATE TABLE customers (
                    id INT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE,
                    phone VARCHAR(20),
                    balance FLOAT DEFAULT 0.0,
                    created_at DATETIME,
                    is_active BOOLEAN DEFAULT TRUE
                );
            """)
            print("✓ Created customers table")
        else:
            # Add is_active column if table exists but column doesn't
            try:
                # Try to add the column (will fail if it already exists, which is fine)
                executor.execute("ALTER TABLE customers ADD COLUMN is_active BOOLEAN DEFAULT TRUE;")
                # Update existing records to be active
                executor.execute("UPDATE customers SET is_active = TRUE WHERE is_active IS NULL;")
            except:
                pass  # Column might already exist

        if not db.table_exists('merchants'):
            executor.execute("""
                CREATE TABLE merchants (
                    id INT PRIMARY KEY,
                    business_name VARCHAR(100) NOT NULL,
                    category VARCHAR(50),
                    mpesa_paybill VARCHAR(20),
                    email VARCHAR(100),
                    total_transactions FLOAT DEFAULT 0.0
                );
            """)
            print("✓ Created merchants table")

        if not db.table_exists('transactions'):
            executor.execute("""
                CREATE TABLE transactions (
                    id INT PRIMARY KEY,
                    customer_id INT NOT NULL,
                    merchant_id INT NOT NULL,
                    amount FLOAT NOT NULL,
                    payment_method VARCHAR(50),
                    status VARCHAR(20),
                    transaction_date DATETIME,
                    date_added DATETIME,
                    added_by VARCHAR(100),
                    source VARCHAR(50)
                );
            """)
            print("✓ Created transactions table")

            # Create indexes for better performance
            try:
                executor.execute("CREATE INDEX idx_trans_customer ON transactions (customer_id);")
                executor.execute("CREATE INDEX idx_trans_merchant ON transactions (merchant_id);")
                print("✓ Created indexes")
            except:
                pass  # Indexes might already exist

        print("✓ Database initialized successfully (tables created, no data loaded)")

    except Exception as e:
        print(f"Error initializing database: {str(e)}")


@app.route('/')
def serve_frontend():
    """Serve React frontend"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'database': db.name})


@app.route('/api/query', methods=['POST'])
def execute_query():
    """Execute a SQL query"""
    try:
        data = request.get_json()
        query = data.get('query')

        if not query:
            return jsonify({'error': 'No query provided'}), 400

        result = executor.execute(query)

        return jsonify({
            'columns': result.columns,
            'rows': result.rows,
            'message': result.message,
            'row_count': result.row_count
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/customers', methods=['GET', 'POST'])
def customers():
    """Get all customers or create new customer"""
    try:
        if request.method == 'GET':
            # Get all customers and filter active ones in Python
            result = executor.execute("SELECT * FROM customers;")
            # Filter to only active customers
            active_customers = [
                row for row in result.rows
                if row.get('is_active') is True or row.get('is_active') is None
            ]
            return jsonify({'customers': active_customers})

        elif request.method == 'POST':
            data = request.get_json()

            # Get next ID
            result = executor.execute("SELECT * FROM customers;")
            next_id = max([row['id'] for row in result.rows], default=0) + 1

            query = f"""
                INSERT INTO customers (id, name, email, phone, balance, is_active)
                VALUES ({next_id}, '{data['name']}', '{data['email']}',
                        '{data.get('phone', '')}', {data.get('balance', 0.0)}, TRUE);
            """

            executor.execute(query)

            return jsonify({'message': 'Customer created', 'id': next_id}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/customers/<int:customer_id>', methods=['GET', 'PUT', 'DELETE'])
def customer_detail(customer_id):
    """Get, update, or delete a specific customer"""
    try:
        if request.method == 'GET':
            result = executor.execute(f"SELECT * FROM customers WHERE id = {customer_id};")
            if not result.rows:
                return jsonify({'error': 'Customer not found'}), 404
            return jsonify(result.rows[0])

        elif request.method == 'PUT':
            data = request.get_json()
            updates = []

            if 'name' in data:
                updates.append(f"name = '{data['name']}'")
            if 'email' in data:
                updates.append(f"email = '{data['email']}'")
            if 'phone' in data:
                updates.append(f"phone = '{data['phone']}'")
            if 'balance' in data:
                updates.append(f"balance = {data['balance']}")

            if updates:
                query = f"UPDATE customers SET {', '.join(updates)} WHERE id = {customer_id};"
                executor.execute(query)

            return jsonify({'message': 'Customer updated'})

        elif request.method == 'DELETE':
            # Check if customer has transactions
            transactions_result = executor.execute(f"SELECT * FROM transactions WHERE customer_id = {customer_id};")

            if len(transactions_result.rows) > 0:
                # Customer has transactions - soft delete (mark as inactive)
                executor.execute(f"UPDATE customers SET is_active = FALSE WHERE id = {customer_id};")
                return jsonify({
                    'message': f'Customer deactivated (has {len(transactions_result.rows)} transaction(s)). Customer hidden from UI but preserved in database for data integrity.',
                    'soft_delete': True,
                    'transaction_count': len(transactions_result.rows)
                })
            else:
                # No transactions - can safely hard delete
                executor.execute(f"DELETE FROM customers WHERE id = {customer_id};")
                return jsonify({'message': 'Customer deleted', 'soft_delete': False})

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/merchants', methods=['GET', 'POST'])
def merchants():
    """Get all merchants or create new merchant"""
    try:
        if request.method == 'GET':
            result = executor.execute("SELECT * FROM merchants;")
            return jsonify({'merchants': result.rows})

        elif request.method == 'POST':
            data = request.get_json()

            # Get next ID
            result = executor.execute("SELECT * FROM merchants;")
            next_id = max([row['id'] for row in result.rows], default=0) + 1

            query = f"""
                INSERT INTO merchants (id, business_name, category, mpesa_paybill, email, total_transactions)
                VALUES ({next_id}, '{data['business_name']}', '{data.get('category', '')}',
                        '{data.get('mpesa_paybill', '')}', '{data.get('email', '')}', 0.0);
            """

            executor.execute(query)

            return jsonify({'message': 'Merchant created', 'id': next_id}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/transactions', methods=['GET', 'POST'])
def transactions():
    """Get all transactions or create new transaction"""
    try:
        if request.method == 'GET':
            # First check if tables exist and have data
            try:
                # Check if transactions table has data
                check_result = executor.execute("SELECT * FROM transactions;")
                print(f"📊 Transactions table has {len(check_result.rows)} rows")

                if len(check_result.rows) == 0:
                    print("⚠️  No transactions in database")
                    return jsonify({'transactions': []})

                # Get transactions with customer and merchant details using JOIN
                query = "SELECT transactions.id, transactions.customer_id, transactions.merchant_id, transactions.amount, transactions.payment_method, transactions.status, transactions.date_added, transactions.added_by, transactions.source, customers.name, merchants.business_name FROM transactions INNER JOIN customers ON transactions.customer_id = customers.id INNER JOIN merchants ON transactions.merchant_id = merchants.id;"

                print(f"🔍 Executing JOIN query: {query[:100]}...")
                result = executor.execute(query)
                print(f"✅ JOIN query returned {len(result.rows)} rows")

                # Log first row for debugging
                if result.rows:
                    print(f"📄 First row: {result.rows[0]}")

                return jsonify({'transactions': result.rows})
            except Exception as join_error:
                # If JOIN fails, try to return simple transaction data
                print(f"❌ JOIN query failed: {join_error}")
                import traceback
                traceback.print_exc()

                # Fallback: return transactions without JOIN
                try:
                    print("🔄 Attempting fallback: simple SELECT")
                    simple_result = executor.execute("SELECT * FROM transactions;")
                    print(f"✅ Fallback returned {len(simple_result.rows)} rows")
                    return jsonify({'transactions': simple_result.rows})
                except Exception as fallback_error:
                    print(f"❌ Fallback also failed: {fallback_error}")
                    return jsonify({'transactions': []})

        elif request.method == 'POST':
            data = request.get_json()

            # Validate customer has sufficient balance
            customer_result = executor.execute(f"SELECT balance FROM customers WHERE id = {data['customer_id']};")
            if not customer_result.rows:
                return jsonify({'error': 'Customer not found'}), 404

            current_balance = float(customer_result.rows[0]['balance'])
            transaction_amount = float(data['amount'])

            if current_balance < transaction_amount:
                return jsonify({
                    'error': f'Insufficient balance. Customer has KES {current_balance:.2f}, but transaction requires KES {transaction_amount:.2f}'
                }), 400

            # Validate merchant exists
            merchant_result = executor.execute(f"SELECT id FROM merchants WHERE id = {data['merchant_id']};")
            if not merchant_result.rows:
                return jsonify({'error': 'Merchant not found'}), 404

            # Get next ID
            result = executor.execute("SELECT * FROM transactions;")
            next_id = max([row['id'] for row in result.rows], default=0) + 1

            # Get current datetime and user info
            from datetime import datetime
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            added_by = data.get('added_by', 'Web User')
            source = data.get('source', 'Web App')

            # Create transaction
            query = f"""
                INSERT INTO transactions (id, customer_id, merchant_id, amount, payment_method, status, date_added, added_by, source)
                VALUES ({next_id}, {data['customer_id']}, {data['merchant_id']},
                        {data['amount']}, '{data.get('payment_method', 'M-PESA')}',
                        '{data.get('status', 'completed')}', '{now}', '{added_by}', '{source}');
            """

            executor.execute(query)

            # Update customer balance (deduct)
            new_balance = current_balance - transaction_amount
            executor.execute(f"UPDATE customers SET balance = {new_balance} WHERE id = {data['customer_id']};")

            # Update merchant total
            merchant_total_result = executor.execute(f"SELECT total_transactions FROM merchants WHERE id = {data['merchant_id']};")
            if merchant_total_result.rows:
                current_total = float(merchant_total_result.rows[0]['total_transactions'])
                new_total = current_total + transaction_amount
                executor.execute(f"UPDATE merchants SET total_transactions = {new_total} WHERE id = {data['merchant_id']};")

            return jsonify({'message': 'Transaction created', 'id': next_id}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/stats', methods=['GET'])
def stats():
    """Get database statistics"""
    try:
        # Get counts
        customers_result = executor.execute("SELECT * FROM customers;")
        merchants_result = executor.execute("SELECT * FROM merchants;")
        transactions_result = executor.execute("SELECT * FROM transactions;")

        # Calculate total transaction amount (only completed)
        total_amount = sum(
            float(row.get('amount', 0))
            for row in transactions_result.rows
            if row.get('status') == 'completed'
        )

        # Calculate status breakdown with counts and amounts
        status_breakdown = {
            'completed': {'count': 0, 'amount': 0.0},
            'pending': {'count': 0, 'amount': 0.0},
            'failed': {'count': 0, 'amount': 0.0}
        }

        for row in transactions_result.rows:
            status = row.get('status', 'completed')
            amount = float(row.get('amount', 0))
            if status in status_breakdown:
                status_breakdown[status]['count'] += 1
                status_breakdown[status]['amount'] += amount

        # Get database stats safely - build manually if get_stats() fails
        try:
            db_stats = db.get_stats()
            # Ensure tables dict is populated
            if not db_stats.get('tables') or len(db_stats.get('tables', {})) == 0:
                # Manually build stats from all tables dynamically
                all_tables = db.list_tables()
                db_stats = {
                    'name': db.name,
                    'num_tables': len(all_tables),
                    'tables': {}
                }
                for table_name in all_tables:
                    try:
                        table = db.get_table(table_name)
                        if table:
                            db_stats['tables'][table_name] = {
                                'columns': len(table.columns),
                                'rows': len(table.scan()),
                                'indexes': len(table.indexes),
                                'size_kb': 0.0  # Size calculation can be expensive
                            }
                    except Exception as table_error:
                        print(f"Warning: Could not get stats for table {table_name}: {table_error}")
                        db_stats['tables'][table_name] = {
                            'columns': 0,
                            'rows': 0,
                            'indexes': 0,
                            'size_kb': 0.0
                        }
        except Exception as db_stats_error:
            print(f"Warning: Could not get db_stats: {db_stats_error}")
            import traceback
            traceback.print_exc()
            # Manually build stats from all tables dynamically
            all_tables = db.list_tables()
            db_stats = {
                'name': db.name,
                'num_tables': len(all_tables),
                'tables': {}
            }
            for table_name in all_tables:
                try:
                    table = db.get_table(table_name)
                    if table:
                        db_stats['tables'][table_name] = {
                            'columns': len(table.columns),
                            'rows': len(table.scan()),
                            'indexes': len(table.indexes),
                            'size_kb': 0.0
                        }
                except Exception as table_error:
                    print(f"Warning: Could not get stats for table {table_name}: {table_error}")
                    # Add table name anyway with default stats
                    db_stats['tables'][table_name] = {
                        'columns': 0,
                        'rows': 0,
                        'indexes': 0,
                        'size_kb': 0.0
                    }

        return jsonify({
            'total_customers': len(customers_result.rows),
            'total_merchants': len(merchants_result.rows),
            'total_transactions': len(transactions_result.rows),
            'total_amount': total_amount,
            'status_breakdown': status_breakdown,
            'db_stats': db_stats
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400


@app.route('/api/stats/volume', methods=['GET'])
def stats_volume():
    """Get transaction volume statistics filtered by time period"""
    try:
        from datetime import datetime, timedelta

        period = request.args.get('period', 'all')

        # Get all transactions
        transactions_result = executor.execute("SELECT * FROM transactions;")

        # Filter by date based on period
        now = datetime.now()
        filtered_transactions = []

        # Parse period parameter (can be 'all', 'day', 'month', 'year', or 'day:YYYY-MM-DD', 'month:YYYY-MM', 'year:YYYY')
        period_type = period
        period_value = None
        if ':' in period:
            period_type, period_value = period.split(':', 1)

        for row in transactions_result.rows:
            date_added_str = row.get('date_added') or row.get('transaction_date')
            if not date_added_str:
                # If no date, include it for 'all' period only
                if period_type == 'all':
                    filtered_transactions.append(row)
                continue

            try:
                # Parse date string (format: 'YYYY-MM-DD HH:MM:SS')
                transaction_date = datetime.strptime(date_added_str, '%Y-%m-%d %H:%M:%S')

                if period_type == 'all':
                    filtered_transactions.append(row)
                elif period_type == 'day':
                    if period_value:
                        # Specific date selected
                        selected_date = datetime.strptime(period_value, '%Y-%m-%d').date()
                        if transaction_date.date() == selected_date:
                            filtered_transactions.append(row)
                    else:
                        # Default to today
                        if transaction_date.date() == now.date():
                            filtered_transactions.append(row)
                elif period_type == 'month':
                    if period_value:
                        # Specific month selected (format: YYYY-MM)
                        selected_year, selected_month = map(int, period_value.split('-'))
                        if transaction_date.year == selected_year and transaction_date.month == selected_month:
                            filtered_transactions.append(row)
                    else:
                        # Default to current month
                        if transaction_date.year == now.year and transaction_date.month == now.month:
                            filtered_transactions.append(row)
                elif period_type == 'year':
                    if period_value:
                        # Specific year selected
                        selected_year = int(period_value)
                        if transaction_date.year == selected_year:
                            filtered_transactions.append(row)
                    else:
                        # Default to current year
                        if transaction_date.year == now.year:
                            filtered_transactions.append(row)
            except (ValueError, TypeError) as e:
                # If date parsing fails, include for 'all' period only
                if period_type == 'all':
                    filtered_transactions.append(row)

        # Calculate status breakdown with counts and amounts
        status_breakdown = {
            'completed': {'count': 0, 'amount': 0.0},
            'pending': {'count': 0, 'amount': 0.0},
            'failed': {'count': 0, 'amount': 0.0}
        }

        # Calculate total amount (ALL transactions, all statuses)
        total_amount = 0.0
        for row in filtered_transactions:
            status = row.get('status', 'completed')
            amount = float(row.get('amount', 0))
            total_amount += amount  # Add to total (all transactions)

            # Normalize status to one of the known statuses
            normalized_status = status.lower() if status and status.lower() in status_breakdown else 'completed'

            # Add to status breakdown
            status_breakdown[normalized_status]['count'] += 1
            status_breakdown[normalized_status]['amount'] += amount

        return jsonify({
            'total_amount': total_amount,
            'status_breakdown': status_breakdown
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/load-test-data', methods=['POST'])
def load_test_data():
    """Load test data into the database"""
    try:
        from datetime import datetime, timedelta

        # Check if data already exists
        customers_table = db.get_table('customers')
        if len(customers_table.scan()) > 0:
            return jsonify({'error': 'Test data already exists. Please clear the database first.'}), 400

        # Load customers (25 customers)
        customers_data = [
            (1, 'Alice Mwangi', 'test1@test.com', '+254712345678', 5000.00),
            (2, 'Bob Otieno', 'test2@test.com', '+254723456789', 3500.50),
            (3, 'Carol Njeri', 'test3@test.com', '+254734567890', 7200.00),
            (4, 'David Kimani', 'test4@test.com', '+254745678901', 2800.75),
            (5, 'Eve Wanjiku', 'test5@test.com', '+254756789012', 4500.00),
            (6, 'Frank Ochieng', 'test6@test.com', '+254767890123', 6200.50),
            (7, 'Grace Achieng', 'test7@test.com', '+254778901234', 3800.25),
            (8, 'Henry Mutua', 'test8@test.com', '+254789012345', 5500.00),
            (9, 'Irene Wambui', 'test9@test.com', '+254790123456', 4100.00),
            (10, 'James Kariuki', 'test10@test.com', '+254701234567', 6700.75),
            (11, 'Katherine Muthoni', 'test11@test.com', '+254711111111', 5200.00),
            (12, 'Liam Omondi', 'test12@test.com', '+254722222222', 4300.50),
            (13, 'Mary Wanjala', 'test13@test.com', '+254733333333', 6100.00),
            (14, 'Noah Kipchoge', 'test14@test.com', '+254744444444', 3400.75),
            (15, 'Olivia Chebet', 'test15@test.com', '+254755555555', 4800.00),
            (16, 'Peter Kamau', 'test16@test.com', '+254766666666', 5900.50),
            (17, 'Quinn Adhiambo', 'test17@test.com', '+254777777777', 3600.25),
            (18, 'Rachel Nyambura', 'test18@test.com', '+254788888888', 5400.00),
            (19, 'Samuel Maina', 'test19@test.com', '+254799999999', 4700.00),
            (20, 'Teresa Wairimu', 'test20@test.com', '+254700000000', 6300.75),
            (21, 'Victor Ochieng', 'test21@test.com', '+254710101010', 3900.50),
            (22, 'Winnie Akinyi', 'test22@test.com', '+254720202020', 5600.00),
            (23, 'Xavier Mwangi', 'test23@test.com', '+254730303030', 4200.25),
            (24, 'Yvonne Njeri', 'test24@test.com', '+254740404040', 5800.00),
            (25, 'Zachary Kariuki', 'test25@test.com', '+254750505050', 5100.75),
        ]

        for customer in customers_data:
            executor.execute(f"INSERT INTO customers (id, name, email, phone, balance, is_active) VALUES ({customer[0]}, '{customer[1]}', '{customer[2]}', '{customer[3]}', {customer[4]}, TRUE);")

        # Load merchants (12 merchants)
        merchants_data = [
            (1, 'SuperMart Kenya', 'Retail', '123456', 'test1@merchant.com', 0.0),
            (2, 'Java House', 'Restaurant', '234567', 'test2@merchant.com', 0.0),
            (3, 'Naivas Supermarket', 'Retail', '345678', 'test3@merchant.com', 0.0),
            (4, 'Uber Kenya', 'Transportation', '456789', 'test4@merchant.com', 0.0),
            (5, 'Safaricom Shop', 'Services', '567890', 'test5@merchant.com', 0.0),
            (6, 'KFC Kenya', 'Restaurant', '678901', 'test6@merchant.com', 0.0),
            (7, 'Nakumatt Supermarket', 'Retail', '789012', 'test7@merchant.com', 0.0),
            (8, 'Bolt Kenya', 'Transportation', '890123', 'test8@merchant.com', 0.0),
            (9, 'Pizza Inn', 'Restaurant', '901234', 'test9@merchant.com', 0.0),
            (10, 'Equity Bank', 'Services', '012345', 'test10@merchant.com', 0.0),
            (11, 'Game Stores', 'Retail', '135792', 'test11@merchant.com', 0.0),
            (12, 'DStv Kenya', 'Entertainment', '246813', 'test12@merchant.com', 0.0),
        ]

        for merchant in merchants_data:
            executor.execute(f"INSERT INTO merchants (id, business_name, category, mpesa_paybill, email, total_transactions) VALUES ({merchant[0]}, '{merchant[1]}', '{merchant[2]}', '{merchant[3]}', '{merchant[4]}', {merchant[5]});")

        # Load transactions with mixed statuses (60 transactions)
        now = datetime.now()
        import random
        payment_methods = ['M-PESA', 'Card', 'Bank Transfer', 'Cash']
        statuses = ['completed', 'pending', 'failed']

        transactions_data = []
        trans_id = 1

        # Generate 60 transactions with varied distribution
        for day_offset in range(30):  # Last 30 days
            for _ in range(2):  # 2 transactions per day on average
                customer_id = random.randint(1, 25)
                merchant_id = random.randint(1, 12)
                amount = round(random.uniform(50.0, 2000.0), 2)
                payment_method = random.choice(payment_methods)

                # Weight statuses: 60% completed, 25% pending, 15% failed
                rand = random.random()
                if rand < 0.60:
                    status = 'completed'
                elif rand < 0.85:
                    status = 'pending'
                else:
                    status = 'failed'

                # Vary time within the day
                hours_offset = random.randint(0, 23)
                minutes_offset = random.randint(0, 59)
                transaction_date = now - timedelta(days=day_offset, hours=hours_offset, minutes=minutes_offset)

                transactions_data.append((
                    trans_id, customer_id, merchant_id, amount, payment_method, status, transaction_date
                ))
                trans_id += 1

        # Add some recent transactions (today)
        for _ in range(10):
            customer_id = random.randint(1, 25)
            merchant_id = random.randint(1, 12)
            amount = round(random.uniform(100.0, 1500.0), 2)
            payment_method = random.choice(payment_methods)
            status = random.choice(['completed', 'pending'])
            transaction_date = now - timedelta(hours=random.randint(0, 12), minutes=random.randint(0, 59))

            transactions_data.append((
                trans_id, customer_id, merchant_id, amount, payment_method, status, transaction_date
            ))
            trans_id += 1

        for trans in transactions_data:
            date_str = trans[6].strftime('%Y-%m-%d %H:%M:%S')
            executor.execute(f"INSERT INTO transactions (id, customer_id, merchant_id, amount, payment_method, status, date_added, added_by, source) VALUES ({trans[0]}, {trans[1]}, {trans[2]}, {trans[3]}, '{trans[4]}', '{trans[5]}', '{date_str}', 'Test Data Loader', 'Test Data');")

        # Update merchant totals (calculate in Python since SUM() might not be supported)
        for merchant_id in range(1, 13):
            merchant_transactions = executor.execute(f"SELECT amount FROM transactions WHERE merchant_id = {merchant_id} AND status = 'completed';")
            total = sum(float(row.get('amount', 0)) for row in merchant_transactions.rows)
            if total > 0:
                executor.execute(f"UPDATE merchants SET total_transactions = {total} WHERE id = {merchant_id};")

        return jsonify({
            'message': 'Test data loaded successfully',
            'customers': len(customers_data),
            'merchants': len(merchants_data),
            'transactions': len(transactions_data)
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400


@app.route('/api/debug/tables', methods=['GET'])
def debug_tables():
    """Debug endpoint to check table contents"""
    try:
        debug_info = {}

        # Check each table
        for table_name in ['customers', 'merchants', 'transactions']:
            result = executor.execute(f"SELECT * FROM {table_name};")
            debug_info[table_name] = {
                'row_count': len(result.rows),
                'rows': result.rows[:5]  # First 5 rows only
            }

        return jsonify(debug_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Starting PyRelDB Payment Management API")
    print("=" * 60)

    # Initialize database
    init_demo_database()

    print("\n📊 API Endpoints:")
    print("  GET  /api/health")
    print("  POST /api/query")
    print("  GET  /api/customers")
    print("  POST /api/customers")
    print("  GET  /api/merchants")
    print("  POST /api/merchants")
    print("  GET  /api/transactions")
    print("  POST /api/transactions")
    print("  GET  /api/stats")
    print("\n🌐 Server running on http://localhost:5000 (External: http://localhost:8080)")
    print("=" * 60)
    print()

    app.run(debug=True, host='0.0.0.0', port=5000)

