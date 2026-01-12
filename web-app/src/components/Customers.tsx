import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Customer } from '../types';
import './Common.css';

interface CustomersProps {
  onUpdate: () => void;
}

interface CustomerFormData {
  name: string;
  email: string;
  phone: string;
  balance: number;
}

const Customers: React.FC<CustomersProps> = ({ onUpdate }) => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [filteredCustomers, setFilteredCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [editingCustomer, setEditingCustomer] = useState<Customer | null>(null);
  const [formData, setFormData] = useState<CustomerFormData>({
    name: '',
    email: '',
    phone: '',
    balance: 0
  });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [itemsPerPage] = useState<number>(10);
  const [showDeleteModal, setShowDeleteModal] = useState<boolean>(false);
  const [customerToDelete, setCustomerToDelete] = useState<Customer | null>(null);
  const [deleteConfirmText, setDeleteConfirmText] = useState<string>('');

  useEffect(() => {
    loadCustomers();
  }, []);

  useEffect(() => {
    filterCustomers();
  }, [customers, searchTerm]);

  const loadCustomers = async () => {
    try {
      const data = await api.getCustomers();
      setCustomers(data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load customers');
      setLoading(false);
    }
  };

  const filterCustomers = () => {
    let filtered = customers;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(customer =>
        customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        customer.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (customer.phone && customer.phone.includes(searchTerm))
      );
    }

    setFilteredCustomers(filtered);
    setCurrentPage(1); // Reset to first page when filtering
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    try {
      if (editingCustomer) {
        await api.updateCustomer(editingCustomer.id, formData);
        setSuccess('Customer updated successfully!');
      } else {
        await api.createCustomer(formData);
        setSuccess('Customer created successfully!');
      }

      setShowModal(false);
      setFormData({ name: '', email: '', phone: '', balance: 0 });
      setEditingCustomer(null);
      loadCustomers();
      onUpdate();
    } catch (err: any) {
      setError(err.response?.data?.error || 'Operation failed');
    }
  };

  const handleEdit = (customer: Customer) => {
    setEditingCustomer(customer);
    setFormData({
      name: customer.name,
      email: customer.email,
      phone: customer.phone || '',
      balance: customer.balance || 0
    });
    setShowModal(true);
  };

  const handleDeleteClick = (customer: Customer) => {
    setCustomerToDelete(customer);
    setDeleteConfirmText('');
    setShowDeleteModal(true);
  };

  const handleDeleteConfirm = async () => {
    if (deleteConfirmText.toLowerCase() !== 'delete') {
      setError('Please type "delete" to confirm');
      return;
    }

    if (!customerToDelete) return;

    try {
      const response = await api.deleteCustomer(customerToDelete.id);
      const responseData = response as any;

      if (responseData?.soft_delete) {
        setSuccess(`Customer deactivated successfully! Customer has ${responseData.transaction_count} transaction(s) and has been hidden from the UI but preserved in the database for data integrity.`);
      } else {
        setSuccess('Customer deleted successfully!');
      }
      setShowDeleteModal(false);
      setCustomerToDelete(null);
      setDeleteConfirmText('');
      loadCustomers();
      onUpdate();
    } catch (err: any) {
      setError(err.response?.data?.error || 'Delete failed');
    }
  };

  const handleDeleteCancel = () => {
    setShowDeleteModal(false);
    setCustomerToDelete(null);
    setDeleteConfirmText('');
    setError(null);
  };

  const openNewModal = () => {
    setEditingCustomer(null);
    setFormData({ name: '', email: '', phone: '', balance: 0 });
    setShowModal(true);
  };

  if (loading) {
    return <div className="loading">Loading customers...</div>;
  }

  // Pagination
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentCustomers = filteredCustomers.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(filteredCustomers.length / itemsPerPage);

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>Customers</h1>
          <p className="page-subtitle">Manage customer accounts and balances ({filteredCustomers.length} total)</p>
        </div>
        <button className="btn btn-primary" onClick={openNewModal}>
          Add Customer
        </button>
      </div>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      <div className="card">
        <div className="table-controls">
          <div className="search-box">
            <input
              type="text"
              placeholder="Search by name, email, or phone..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>
        </div>

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Balance</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {currentCustomers.map((customer) => (
                <tr key={customer.id}>
                  <td>{customer.id}</td>
                  <td>{customer.name}</td>
                  <td>{customer.email}</td>
                  <td>{customer.phone || '-'}</td>
                  <td>KES {parseFloat(String(customer.balance || 0)).toFixed(2)}</td>
                  <td>
                    <div className="action-buttons">
                      <button
                        className="btn-small btn-secondary"
                        onClick={() => handleEdit(customer)}
                      >
                        Edit
                      </button>
                      <button
                        className="btn-small btn-danger"
                        onClick={() => handleDeleteClick(customer)}
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredCustomers.length === 0 && (
          <div className="empty-state">
            <p>{searchTerm ? 'No customers match your search.' : 'No customers found. Add your first customer!'}</p>
          </div>
        )}

        {filteredCustomers.length > itemsPerPage && (
          <div className="pagination">
            <button
              className="pagination-btn"
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
            >
              Previous
            </button>
            <div className="pagination-info">
              Page {currentPage} of {totalPages} ({filteredCustomers.length} customers)
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
            <h2>{editingCustomer ? 'Edit Customer' : 'Add New Customer'}</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Name *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Email *</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Phone</label>
                <input
                  type="text"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  placeholder="+254712345678"
                />
              </div>
              <div className="form-group">
                <label>Balance (KES)</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.balance}
                  onChange={(e) => setFormData({ ...formData, balance: parseFloat(e.target.value) || 0 })}
                  onFocus={(e) => e.target.select()}
                  placeholder="0.00"
                />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  {editingCustomer ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showDeleteModal && customerToDelete && (
        <div className="modal-overlay" onClick={handleDeleteCancel}>
          <div className="modal modal-danger" onClick={(e) => e.stopPropagation()}>
            <h2>Delete Customer</h2>
            <div className="delete-warning">
              <p><strong>Warning:</strong> This action will hide the customer from the UI.</p>
              <p>Are you sure you want to remove <strong>{customerToDelete.name}</strong>?</p>
              <p style={{fontSize: '0.9rem', marginTop: '0.75rem'}}>
                <strong>Note:</strong> If this customer has transactions, they will be hidden from the UI but preserved in the database for data integrity. Customers without transactions will be permanently deleted.
              </p>
              <p className="delete-instruction">
                Type <strong>"delete"</strong> to confirm:
              </p>
            </div>
            <div className="form-group">
              <input
                type="text"
                value={deleteConfirmText}
                onChange={(e) => setDeleteConfirmText(e.target.value)}
                placeholder="Type 'delete' to confirm"
                className="delete-confirm-input"
                autoFocus
              />
            </div>
            {error && <div className="error" style={{marginBottom: '1rem'}}>{error}</div>}
            <div className="modal-actions">
              <button type="button" className="btn btn-secondary" onClick={handleDeleteCancel}>
                Cancel
              </button>
              <button
                type="button"
                className="btn btn-danger"
                onClick={handleDeleteConfirm}
                disabled={deleteConfirmText.toLowerCase() !== 'delete'}
              >
                Delete Customer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Customers;

