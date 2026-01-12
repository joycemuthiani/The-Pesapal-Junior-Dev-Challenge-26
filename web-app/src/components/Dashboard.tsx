import React, { useState, useEffect } from 'react';
import './Dashboard.css';
import { DatabaseStats } from '../types';
import { api } from '../services/api';

interface DashboardProps {
  stats: DatabaseStats | null;
  loading: boolean;
  onUpdate?: () => void;
}

type TimePeriod = 'day' | 'month' | 'year' | 'all';

interface VolumeStats {
  total_amount: number;
  status_breakdown: DatabaseStats['status_breakdown'];
}

const Dashboard: React.FC<DashboardProps> = ({ stats, loading, onUpdate }) => {
  const [selectedPeriod, setSelectedPeriod] = useState<TimePeriod>('all');
  const [volumeStats, setVolumeStats] = useState<VolumeStats | null>(null);
  const [volumeLoading, setVolumeLoading] = useState<boolean>(false);
  const [loadingTestData, setLoadingTestData] = useState<boolean>(false);
  const [testDataMessage, setTestDataMessage] = useState<string | null>(null);
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [selectedMonth, setSelectedMonth] = useState<string>('');
  const [selectedYear, setSelectedYear] = useState<string>('');
  const [showDatePicker, setShowDatePicker] = useState<boolean>(false);
  const [showMonthPicker, setShowMonthPicker] = useState<boolean>(false);
  const [showYearPicker, setShowYearPicker] = useState<boolean>(false);

  useEffect(() => {
    // Only load if we have the required data for the selected period
    if (selectedPeriod === 'all') {
      loadVolumeStats();
    } else if (selectedPeriod === 'day' && selectedDate) {
      loadVolumeStats();
    } else if (selectedPeriod === 'month' && selectedMonth) {
      loadVolumeStats();
    } else if (selectedPeriod === 'year' && selectedYear) {
      loadVolumeStats();
    }
  }, [selectedPeriod, selectedDate, selectedMonth, selectedYear]);

  const loadVolumeStats = async () => {
    setVolumeLoading(true);
    try {
      let periodParam: string = selectedPeriod;
      if (selectedPeriod === 'day' && selectedDate) {
        periodParam = `day:${selectedDate}`;
      } else if (selectedPeriod === 'month' && selectedMonth) {
        periodParam = `month:${selectedMonth}`;
      } else if (selectedPeriod === 'year' && selectedYear) {
        periodParam = `year:${selectedYear}`;
      }
      const data = await api.getVolumeStats(periodParam);
      setVolumeStats(data);
    } catch (error) {
      console.error('Error loading volume stats:', error);
      // Fallback to main stats if volume endpoint fails
      if (stats) {
        setVolumeStats({
          total_amount: stats.total_amount,
          status_breakdown: stats.status_breakdown
        });
      }
    } finally {
      setVolumeLoading(false);
    }
  };

  const handlePeriodClick = (period: TimePeriod) => {
    if (period === 'day') {
      setShowDatePicker(true);
      setShowMonthPicker(false);
      setShowYearPicker(false);
      setSelectedPeriod('day');
      if (!selectedDate) {
        // Set default to today
        const today = new Date().toISOString().split('T')[0];
        setSelectedDate(today);
      }
    } else if (period === 'month') {
      setShowDatePicker(false);
      setShowMonthPicker(true);
      setShowYearPicker(false);
      setSelectedPeriod('month');
      if (!selectedMonth) {
        // Set default to current month
        const now = new Date();
        const monthValue = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
        setSelectedMonth(monthValue);
      }
    } else if (period === 'year') {
      setShowDatePicker(false);
      setShowMonthPicker(false);
      setShowYearPicker(true);
      setSelectedPeriod('year');
      if (!selectedYear) {
        // Set default to current year
        setSelectedYear(String(new Date().getFullYear()));
      }
    } else {
      // 'all'
      setShowDatePicker(false);
      setShowMonthPicker(false);
      setShowYearPicker(false);
      setSelectedDate('');
      setSelectedMonth('');
      setSelectedYear('');
      setSelectedPeriod('all');
    }
  };

  const handleLoadTestData = async () => {
    if (!window.confirm('This will load test data (10 customers, 6 merchants, 20 transactions with mixed statuses). Continue?')) {
      return;
    }

    setLoadingTestData(true);
    setTestDataMessage(null);
    try {
      const result = await api.loadTestData();
      setTestDataMessage(`Test data loaded successfully! ${result.customers} customers, ${result.merchants} merchants, ${result.transactions} transactions.`);
      // Refresh stats if callback provided
      if (onUpdate) {
        onUpdate();
      }
      // Reload the page to show new data
      setTimeout(() => {
        window.location.reload();
      }, 2000);
    } catch (error: any) {
      setTestDataMessage(error.response?.data?.error || 'Failed to load test data');
    } finally {
      setLoadingTestData(false);
    }
  };
  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  if (!stats) {
    return <div className="error">Failed to load statistics</div>;
  }

  return (
    <div className="dashboard">
      <div className="hero-section">
        <div className="hero-content">
          <div className="hero-left">
            <div className="hero-badge">Pesapal Challenge '26</div>
            <h1 className="hero-title">Payment Management Platform</h1>
            <p className="hero-subtitle">
              Manage customers, merchants, and transactions
            </p>
            <div className="hero-tags">
              <span className="tag">Real-time Processing</span>
              <span className="tag">Smart Queries</span>
              <span className="tag">Data Integrity</span>
              <span className="tag">Fast Performance</span>
            </div>
            {stats && stats.total_customers === 0 && stats.total_merchants === 0 && (
              <div style={{marginTop: '1.5rem'}}>
                <button
                  className="btn btn-primary"
                  onClick={handleLoadTestData}
                  disabled={loadingTestData}
                  style={{fontSize: '0.9rem', padding: '0.75rem 1.5rem'}}
                >
                  {loadingTestData ? 'Loading Test Data...' : 'Load Test Data'}
                </button>
                {testDataMessage && (
                  <div style={{
                    marginTop: '1rem',
                    padding: '0.75rem',
                    borderRadius: '8px',
                    background: testDataMessage.includes('error') || testDataMessage.includes('Failed')
                      ? '#ffe0e0'
                      : '#d3f9d8',
                    color: testDataMessage.includes('error') || testDataMessage.includes('Failed')
                      ? '#c92a2a'
                      : '#2b8a3e',
                    fontSize: '0.9rem'
                  }}>
                    {testDataMessage}
                  </div>
                )}
              </div>
            )}
          </div>
          <div className="hero-right">
            <div className="code-preview">
              <div className="code-header">
                <span className="code-dot"></span>
                <span className="code-dot"></span>
                <span className="code-dot"></span>
              </div>
              <div className="code-content">
                <div className="code-line"><span className="keyword">SELECT</span> customers.name, transactions.amount</div>
                <div className="code-line"><span className="keyword">FROM</span> transactions</div>
                <div className="code-line"><span className="keyword">INNER JOIN</span> customers</div>
                <div className="code-line"><span className="keyword">ON</span> transactions.customer_id = customers.id;</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card card">
          <div className="stat-info">
            <h3>Total Customers</h3>
            <p className="stat-number">{stats.total_customers}</p>
            <p className="stat-description">Active customer accounts</p>
          </div>
        </div>

        <div className="stat-card card">
          <div className="stat-info">
            <h3>Total Merchants</h3>
            <p className="stat-number">{stats.total_merchants}</p>
            <p className="stat-description">Registered merchants</p>
          </div>
        </div>

        <div className="stat-card card">
          <div className="stat-info">
            <h3>Total Transactions</h3>
            <p className="stat-number">{stats.total_transactions}</p>
            <p className="stat-description">Completed payments</p>
          </div>
        </div>

        <div className="stat-card card highlight">
          <div className="stat-info">
            <div className="volume-header">
              <h3>Transaction Volume</h3>
              <div className="period-filters">
                <div className="period-filter-group">
                  <button
                    className={`period-btn ${selectedPeriod === 'day' ? 'active' : ''}`}
                    onClick={() => handlePeriodClick('day')}
                  >
                    Day
                  </button>
                  {showDatePicker && (
                    <input
                      type="date"
                      value={selectedDate}
                      onChange={(e) => {
                        if (e.target.value) {
                          setSelectedDate(e.target.value);
                          setSelectedPeriod('day');
                        }
                      }}
                      className="date-picker-input"
                      max={new Date().toISOString().split('T')[0]}
                    />
                  )}
                </div>
                <div className="period-filter-group">
                  <button
                    className={`period-btn ${selectedPeriod === 'month' ? 'active' : ''}`}
                    onClick={() => handlePeriodClick('month')}
                  >
                    Month
                  </button>
                  {showMonthPicker && (
                    <input
                      type="month"
                      value={selectedMonth}
                      onChange={(e) => {
                        if (e.target.value) {
                          setSelectedMonth(e.target.value);
                          setSelectedPeriod('month');
                        }
                      }}
                      className="date-picker-input"
                      max={`${new Date().getFullYear()}-${String(new Date().getMonth() + 1).padStart(2, '0')}`}
                    />
                  )}
                </div>
                <div className="period-filter-group">
                  <button
                    className={`period-btn ${selectedPeriod === 'year' ? 'active' : ''}`}
                    onClick={() => handlePeriodClick('year')}
                  >
                    Year
                  </button>
                  {showYearPicker && (
                    <input
                      type="number"
                      value={selectedYear}
                      onChange={(e) => {
                        if (e.target.value) {
                          setSelectedYear(e.target.value);
                          setSelectedPeriod('year');
                        }
                      }}
                      onBlur={() => {
                        if (selectedYear) {
                          loadVolumeStats();
                        }
                      }}
                      className="date-picker-input year-input"
                      placeholder="YYYY"
                      min="2020"
                      max={new Date().getFullYear()}
                    />
                  )}
                </div>
                <button
                  className={`period-btn ${selectedPeriod === 'all' ? 'active' : ''}`}
                  onClick={() => handlePeriodClick('all')}
                >
                  All
                </button>
              </div>
            </div>
            <p className="stat-number">
              {volumeLoading ? 'Loading...' : `KES ${volumeStats?.total_amount?.toFixed(2) || stats?.total_amount?.toFixed(2) || '0.00'}`}
            </p>

            <div className="status-tree">
              {volumeLoading ? (
                <div className="tree-item">
                  <span className="tree-text">Loading...</span>
                </div>
              ) : (
                <>
                  <div className="tree-item">
                    <span className="tree-text">├─ {volumeStats?.status_breakdown.completed.count || stats?.status_breakdown.completed.count || 0} Completed (KES {(volumeStats?.status_breakdown.completed.amount || stats?.status_breakdown.completed.amount || 0).toFixed(2)})</span>
                  </div>
                  <div className="tree-item">
                    <span className="tree-text">├─ {volumeStats?.status_breakdown.pending.count || stats?.status_breakdown.pending.count || 0} Pending (KES {(volumeStats?.status_breakdown.pending.amount || stats?.status_breakdown.pending.amount || 0).toFixed(2)})</span>
                  </div>
                  <div className="tree-item">
                    <span className="tree-text">└─ {volumeStats?.status_breakdown.failed.count || stats?.status_breakdown.failed.count || 0} Failed (KES {(volumeStats?.status_breakdown.failed.amount || stats?.status_breakdown.failed.amount || 0).toFixed(2)})</span>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="features-grid">
        <div className="feature-card card">
          <h3>Custom RDBMS</h3>
          <ul>
            <li>Built from scratch in Python</li>
            <li>File-based persistence with JSON</li>
            <li>Support for multiple data types</li>
            <li>ACID-compliant transactions</li>
          </ul>
        </div>

        <div className="feature-card card">
          <h3>B-tree Indexing</h3>
          <ul>
            <li>O(log n) search complexity</li>
            <li>Automatic index creation</li>
            <li>Range query support</li>
            <li>Primary and unique keys</li>
          </ul>
        </div>

        <div className="feature-card card">
          <h3>SQL Parser</h3>
          <ul>
            <li>Full SQL syntax support</li>
            <li>Tokenization and parsing</li>
            <li>Query optimization</li>
            <li>Error handling</li>
          </ul>
        </div>

        <div className="feature-card card">
          <h3>JOIN Operations</h3>
          <ul>
            <li>INNER JOIN support</li>
            <li>LEFT JOIN support</li>
            <li>Multi-table queries</li>
            <li>Complex conditions</li>
          </ul>
        </div>
      </div>

      <div className="db-info card">
        <h2>Database Statistics</h2>
        <div className="db-stats">
          <div className="db-stat">
            <span className="db-stat-label">Database Name:</span>
            <span className="db-stat-value">{stats.db_stats.name}</span>
          </div>
          <div className="db-stat">
            <span className="db-stat-label">Total Tables:</span>
            <span className="db-stat-value">{stats.db_stats.num_tables}</span>
          </div>
          {stats.db_stats.tables && (
            <div className="db-stat">
              <span className="db-stat-label">Table Names:</span>
              <span className="db-stat-value">
                {Object.keys(stats.db_stats.tables).join(', ')}
              </span>
            </div>
          )}
          {stats.db_stats.tables && Object.entries(stats.db_stats.tables).map(([tableName, tableStats]) => (
            <div key={tableName} className="table-stat">
              <h4>{tableName}</h4>
              <div className="table-stat-details">
                <span>Columns: {tableStats.columns}</span>
                <span>Rows: {tableStats.rows}</span>
                <span>Indexes: {tableStats.indexes}</span>
                <span>Size: {tableStats.size_kb.toFixed(2)} KB</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="tech-stack card">
        <h2>Technology Stack</h2>
        <div className="tech-grid">
          <div className="tech-item">
            <h4>Backend</h4>
            <p>Python 3.11+</p>
            <p>Flask REST API</p>
            <p>Custom SQL Parser</p>
          </div>
          <div className="tech-item">
            <h4>Database</h4>
            <p>Custom RDBMS</p>
            <p>B-tree Indexing</p>
            <p>JSON Storage</p>
          </div>
          <div className="tech-item">
            <h4>Frontend</h4>
            <p>React 18</p>
            <p>TypeScript</p>
            <p>Responsive Design</p>
          </div>
          <div className="tech-item">
            <h4>Features</h4>
            <p>CRUD Operations</p>
            <p>JOIN Queries</p>
            <p>Real-time Stats</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

