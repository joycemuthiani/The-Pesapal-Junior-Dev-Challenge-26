import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { QueryResult } from '../types';
import './QueryConsole.css';

interface ExampleQuery {
  title: string;
  query: string;
}

const RECENT_QUERIES_KEY = 'sql_console_recent_queries';
const MAX_RECENT_QUERIES = 5;

const QueryConsole: React.FC = () => {
  const [query, setQuery] = useState<string>('');
  const [result, setResult] = useState<QueryResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [recentQueries, setRecentQueries] = useState<string[]>([]);

  const exampleQueries: ExampleQuery[] = [
    {
      title: 'Select all customers',
      query: 'SELECT * FROM customers;'
    },
    {
      title: 'Customers with balance > 3000',
      query: 'SELECT * FROM customers WHERE balance > 3000;'
    },
    {
      title: 'JOIN: Transactions with customer names',
      query: `SELECT transactions.id, customers.name, merchants.business_name, transactions.amount FROM transactions INNER JOIN customers ON transactions.customer_id = customers.id INNER JOIN merchants ON transactions.merchant_id = merchants.id;`
    },
    {
      title: 'Create new table',
      query: `CREATE TABLE products (
  id INT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  price FLOAT,
  category VARCHAR(50)
);`
    },
    {
      title: 'Insert data',
      query: "INSERT INTO customers (id, name, email, balance) VALUES (10, 'Test User', 'test@example.com', 1000.00);"
    },
    {
      title: 'Update customer balance',
      query: "UPDATE customers SET balance = 5500.00 WHERE id = 1;"
    },
    {
      title: 'Create index',
      query: "CREATE INDEX idx_customer_email ON customers (email);"
    }
  ];

  // Load recent queries from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(RECENT_QUERIES_KEY);
    if (stored) {
      try {
        setRecentQueries(JSON.parse(stored));
      } catch (e) {
        // If parsing fails, start with empty array
        setRecentQueries([]);
      }
    }
  }, []);

  // Save recent queries to localStorage whenever they change
  useEffect(() => {
    if (recentQueries.length > 0) {
      localStorage.setItem(RECENT_QUERIES_KEY, JSON.stringify(recentQueries));
    }
  }, [recentQueries]);

  const addToRecentQueries = (queryText: string) => {
    const trimmedQuery = queryText.trim();
    if (!trimmedQuery) return;

    setRecentQueries((prev: string[]) => {
      // Remove if already exists (to avoid duplicates)
      const filtered = prev.filter((q: string) => q !== trimmedQuery);
      // Add to beginning and limit to MAX_RECENT_QUERIES
      return [trimmedQuery, ...filtered].slice(0, MAX_RECENT_QUERIES);
    });
  };

  const executeQuery = async () => {
    if (!query.trim()) {
      setError('Please enter a query');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await api.executeQuery(query);
      setResult(data);
      // Add to recent queries on successful execution
      addToRecentQueries(query);
      setLoading(false);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Query execution failed');
      setLoading(false);
    }
  };

  const executeRecentQuery = (recentQuery: string) => {
    setQuery(recentQuery);
    // Auto-execute after a short delay to allow state update
    setTimeout(() => {
      const trimmedQuery = recentQuery.trim();
      if (trimmedQuery) {
        setLoading(true);
        setError(null);
        setResult(null);
        api.executeQuery(trimmedQuery)
          .then((data) => {
            setResult(data);
            // Move to top of recent queries
            addToRecentQueries(trimmedQuery);
            setLoading(false);
          })
          .catch((err: any) => {
            setError(err.response?.data?.error || 'Query execution failed');
            setLoading(false);
          });
      }
    }, 100);
  };

  const truncateQuery = (queryText: string, maxWords: number = 5): string => {
    const words = queryText.trim().split(/\s+/);
    if (words.length <= maxWords) {
      return queryText;
    }
    return words.slice(0, maxWords).join(' ') + '...';
  };

  const setExampleQuery = (exampleQuery: string) => {
    setQuery(exampleQuery);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Execute on Ctrl+Enter or Cmd+Enter
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      executeQuery();
    }
  };

  return (
    <div className="query-console">
      <div className="console-header">
        <div>
          <h1>SQL Console</h1>
          <p className="page-subtitle">Execute SQL queries directly on the database</p>
        </div>
      </div>

      <div className="console-grid">
        <div className="query-section card">
          <div className="section-header">
            <h3>Query Editor</h3>
            <span className="hint">Press Ctrl+Enter to execute</span>
          </div>

          <textarea
            className="query-input"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Enter your SQL query here..."
            rows={10}
          />

          <div className="query-actions">
            <button
              className="btn btn-primary"
              onClick={executeQuery}
              disabled={loading}
            >
              {loading ? 'Executing...' : 'Execute Query'}
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => setQuery('')}
            >
              Clear
            </button>
          </div>

          {error && <div className="error">{error}</div>}

          {result && (
            <div className="result-section">
              <h3>Result</h3>

              {result.message && (
                <div className="success">{result.message}</div>
              )}

              {result.rows && result.rows.length > 0 && (
                <div className="result-table-container">
                  <table className="result-table">
                    <thead>
                      <tr>
                        {result.columns.map((col, idx) => (
                          <th key={idx}>{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {result.rows.map((row, rowIdx) => (
                        <tr key={rowIdx}>
                          {result.columns.map((col, colIdx) => (
                            <td key={colIdx}>{String(row[col] ?? '')}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  <div className="result-info">
                    {result.row_count} row(s) returned
                  </div>
                </div>
              )}

              {result.rows && result.rows.length === 0 && !result.message && (
                <div className="empty-state">No rows returned</div>
              )}
            </div>
          )}
        </div>

        <div className="examples-section">
          {recentQueries.length > 0 && (
            <div className="card">
              <h3>Recently Executed</h3>
              <p className="examples-subtitle">Click to re-execute a query</p>

              <div className="examples-list">
                {recentQueries.map((recentQuery, idx) => (
                  <div
                    key={idx}
                    className="example-item recent-query-item"
                    onClick={() => executeRecentQuery(recentQuery)}
                    title={recentQuery}
                  >
                    <div className="example-query recent-query-text">
                      {truncateQuery(recentQuery)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="card">
            <h3>Example Queries</h3>
            <p className="examples-subtitle">Click to load an example query</p>

            <div className="examples-list">
              {exampleQueries.map((example, idx) => (
                <div
                  key={idx}
                  className="example-item"
                  onClick={() => setExampleQuery(example.query)}
                >
                  <div className="example-title">{example.title}</div>
                  <pre className="example-query">{example.query}</pre>
                </div>
              ))}
            </div>
          </div>

          <div className="card info-card">
            <h3>Supported SQL</h3>
            <ul className="sql-features">
              <li><strong>DDL:</strong> CREATE TABLE, DROP TABLE, CREATE INDEX</li>
              <li><strong>DML:</strong> INSERT, UPDATE, DELETE</li>
              <li><strong>DQL:</strong> SELECT with WHERE, JOIN, ORDER BY, LIMIT</li>
              <li><strong>Data Types:</strong> INT, VARCHAR, FLOAT, BOOLEAN, DATETIME</li>
              <li><strong>Constraints:</strong> PRIMARY KEY, UNIQUE, NOT NULL</li>
              <li><strong>Joins:</strong> INNER JOIN, LEFT JOIN</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QueryConsole;

