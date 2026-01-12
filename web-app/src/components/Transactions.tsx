import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Transaction, Customer, Merchant } from '../types';
import './Common.css';

interface TransactionsProps {
  onUpdate: () => void;
}

interface TransactionFormData {
  customer_id: string;
  merchant_id: string;
  amount: string;
  payment_method: string;
  status: string;
}

const Transactions: React.FC<TransactionsProps> = ({ onUpdate }) => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [filteredTransactions, setFilteredTransactions] = useState<Transaction[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [merchants, setMerchants] = useState<Merchant[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [formData, setFormData] = useState<TransactionFormData>({
    customer_id: '',
    merchant_id: '',
    amount: '',
    payment_method: 'M-PESA',
    status: 'completed'
  });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [paymentMethodFilter, setPaymentMethodFilter] = useState<string>('all');
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [itemsPerPage] = useState<number>(10);

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    filterTransactions();
  }, [transactions, searchTerm, statusFilter, paymentMethodFilter]);

  const loadData = async () => {
    try {
      // Load customers and merchants separately to ensure dropdowns work
      const custData = await api.getCustomers();
      const merchData = await api.getMerchants();
      setCustomers(custData);
      setMerchants(merchData);

      // Try to load transactions (might fail if empty)
      try {
        const transData = await api.getTransactions();
        console.log('Transactions loaded:', transData); // Debug log
        console.log('Number of transactions:', transData.length); // Debug log
        setTransactions(transData);
      } catch (transErr) {
        console.error('Failed to load transactions:', transErr);
        setTransactions([]);
      }

      setLoading(false);
      setError(null); // Clear any previous errors
    } catch (err) {
      console.error('Failed to load data:', err);
      setError('Failed to load customers and merchants');
      setLoading(false);
    }
  };

  const filterTransactions = () => {
    let filtered = transactions;

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter((t: any) => {
        const status = t.status || t['transactions.status'];
        return status === statusFilter;
      });
    }

    // Payment method filter
    if (paymentMethodFilter !== 'all') {
      filtered = filtered.filter((t: any) => {
        const method = t.payment_method || t['transactions.payment_method'];
        return method === paymentMethodFilter;
      });
    }

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter((t: any) => {
        const customerName = (t.name || t['customers.name'] || '').toLowerCase();
        const merchantName = (t.business_name || t['merchants.business_name'] || '').toLowerCase();
        const amount = String(t.amount || t['transactions.amount'] || '');
        return customerName.includes(searchTerm.toLowerCase()) ||
               merchantName.includes(searchTerm.toLowerCase()) ||
               amount.includes(searchTerm);
      });
    }

    setFilteredTransactions(filtered);
    setCurrentPage(1);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    try {
      await api.createTransaction({
        customer_id: parseInt(formData.customer_id),
        merchant_id: parseInt(formData.merchant_id),
        amount: parseFloat(formData.amount),
        payment_method: formData.payment_method,
        status: formData.status
      });
      setSuccess('Transaction created successfully!');
      setShowModal(false);
      setFormData({
        customer_id: '',
        merchant_id: '',
        amount: '',
        payment_method: 'M-PESA',
        status: 'completed'
      });
      // Reload data and update parent stats
      await loadData();
      onUpdate();
    } catch (err: any) {
      setError(err.response?.data?.error || 'Transaction failed');
    }
  };

  const openNewModal = () => {
    setFormData({
      customer_id: '',
      merchant_id: '',
      amount: '',
      payment_method: 'M-PESA',
      status: 'completed'
    });
    setShowModal(true);
  };

  const getStatusBadge = (status: string): string => {
    const statusColors: Record<string, string> = {
      completed: 'badge-success',
      pending: 'badge-warning',
      failed: 'badge-danger'
    };
    return statusColors[status] || 'badge';
  };

  if (loading) {
    return <div className="loading">Loading transactions...</div>;
  }

  console.log('Rendering transactions:', transactions.length); // Debug

  // Pagination
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentTransactions = filteredTransactions.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(filteredTransactions.length / itemsPerPage);

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>Transactions</h1>
          <p className="page-subtitle">View and process payment transactions ({filteredTransactions.length} total)</p>
        </div>
        <button className="btn btn-primary" onClick={openNewModal}>
          New Transaction
        </button>
      </div>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      <div className="card">
        <div className="info-banner">
          <strong>Database Feature:</strong> This view uses INNER JOIN to combine data from
          transactions, customers, and merchants tables in a single query
        </div>

        <div className="table-controls">
          <div className="search-box">
            <input
              type="text"
              placeholder="Search by customer, merchant, or amount..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>
          <div className="filter-section">
            <div className="filter-group">
              <label className="filter-label">Status:</label>
              <div className="filter-tags">
                {['all', 'completed', 'pending', 'failed'].map(status => (
                  <button
                    key={status}
                    className={`filter-tag ${statusFilter === status ? 'active' : ''}`}
                    onClick={() => setStatusFilter(status)}
                  >
                    {status === 'all' ? 'All' : status.charAt(0).toUpperCase() + status.slice(1)}
                  </button>
                ))}
              </div>
            </div>
            <div className="filter-group">
              <label className="filter-label">Payment:</label>
              <div className="filter-tags">
                {['all', 'M-PESA', 'Card', 'Bank Transfer', 'Cash'].map(method => (
                  <button
                    key={method}
                    className={`filter-tag ${paymentMethodFilter === method ? 'active' : ''}`}
                    onClick={() => setPaymentMethodFilter(method)}
                  >
                    {method === 'all' ? 'All' : method}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {filteredTransactions.length > 0 ? (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Customer</th>
                  <th>Merchant</th>
                  <th>Amount</th>
                  <th>Payment Method</th>
                  <th>Status</th>
                  <th>Date Added</th>
                  <th>Added By</th>
                  <th>Source</th>
                </tr>
              </thead>
              <tbody>
              {currentTransactions.map((transaction: any) => {
                // Handle both joined and non-joined data
                const id = transaction.id || transaction['transactions.id'];
                const customerName = transaction.name || transaction['customers.name'] || `Customer #${transaction.customer_id || transaction['transactions.customer_id']}`;
                const merchantName = transaction.business_name || transaction['merchants.business_name'] || `Merchant #${transaction.merchant_id || transaction['transactions.merchant_id']}`;
                const amount = transaction.amount || transaction['transactions.amount'] || 0;
                const paymentMethod = transaction.payment_method || transaction['transactions.payment_method'];
                const status = transaction.status || transaction['transactions.status'];
                const dateAdded = transaction.date_added || transaction['transactions.date_added'] || '-';
                const addedBy = transaction.added_by || transaction['transactions.added_by'] || '-';
                const source = transaction.source || transaction['transactions.source'] || '-';

                // Format date
                const formatDate = (dateStr: string) => {
                  if (!dateStr || dateStr === '-') return '-';
                  try {
                    const date = new Date(dateStr);
                    return date.toLocaleString('en-US', {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    });
                  } catch {
                    return dateStr;
                  }
                };

                return (
                  <tr key={id}>
                    <td>{id}</td>
                    <td>{customerName}</td>
                    <td>{merchantName}</td>
                    <td>KES {parseFloat(String(amount)).toFixed(2)}</td>
                    <td>
                      <span className="badge">{paymentMethod}</span>
                    </td>
                    <td>
                      <span className={`badge ${getStatusBadge(status)}`}>
                        {status}
                      </span>
                    </td>
                    <td>{formatDate(dateAdded)}</td>
                    <td>{addedBy}</td>
                    <td>
                      <span className="badge badge-info">{source}</span>
                    </td>
                  </tr>
                );
              })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty-state">
            <p>{searchTerm || statusFilter !== 'all' || paymentMethodFilter !== 'all' ? 'No transactions match your filters.' : 'No transactions found. Create your first transaction!'}</p>
            <button className="btn btn-primary" onClick={loadData} style={{marginTop: '1rem'}}>
              Refresh
            </button>
          </div>
        )}

        {filteredTransactions.length > itemsPerPage && (
          <div className="pagination">
            <button
              className="pagination-btn"
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
            >
              Previous
            </button>
            <div className="pagination-info">
              Page {currentPage} of {totalPages}
            </div>
            <button
              className="pagination-btn"
              onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages}
            >
              Next
            </button>
          </div>
        )}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>New Transaction</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Customer *</label>
                <select
                  value={formData.customer_id}
                  onChange={(e) => setFormData({ ...formData, customer_id: e.target.value })}
                  required
                >
                  <option value="">Select customer</option>
                  {customers.map((customer) => (
                    <option key={customer.id} value={customer.id}>
                      {customer.name} (Balance: KES {parseFloat(String(customer.balance || 0)).toFixed(2)})
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Merchant *</label>
                <select
                  value={formData.merchant_id}
                  onChange={(e) => setFormData({ ...formData, merchant_id: e.target.value })}
                  required
                >
                  <option value="">Select merchant</option>
                  {merchants.map((merchant) => (
                    <option key={merchant.id} value={merchant.id}>
                      {merchant.business_name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Amount (KES) *</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  onFocus={(e) => e.target.select()}
                  required
                  min="0.01"
                  placeholder="0.00"
                />
              </div>
              <div className="form-group">
                <label>Payment Method</label>
                <select
                  value={formData.payment_method}
                  onChange={(e) => setFormData({ ...formData, payment_method: e.target.value })}
                >
                  <option value="M-PESA">M-PESA</option>
                  <option value="Card">Card</option>
                  <option value="Bank Transfer">Bank Transfer</option>
                  <option value="Cash">Cash</option>
                </select>
              </div>
              <div className="form-group">
                <label>Status</label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                >
                  <option value="completed">Completed</option>
                  <option value="pending">Pending</option>
                  <option value="failed">Failed</option>
                </select>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-success">
                  Process Transaction
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Transactions;

