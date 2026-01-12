import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Merchant } from '../types';
import './Common.css';

interface MerchantsProps {
  onUpdate: () => void;
}

interface MerchantFormData {
  business_name: string;
  category: string;
  mpesa_paybill: string;
  email: string;
}

const Merchants: React.FC<MerchantsProps> = ({ onUpdate }) => {
  const [merchants, setMerchants] = useState<Merchant[]>([]);
  const [filteredMerchants, setFilteredMerchants] = useState<Merchant[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [formData, setFormData] = useState<MerchantFormData>({
    business_name: '',
    category: '',
    mpesa_paybill: '',
    email: ''
  });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [itemsPerPage] = useState<number>(10);

  useEffect(() => {
    loadMerchants();
  }, []);

  useEffect(() => {
    filterMerchants();
  }, [merchants, searchTerm, selectedCategory]);

  const loadMerchants = async () => {
    try {
      const data = await api.getMerchants();
      setMerchants(data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load merchants');
      setLoading(false);
    }
  };

  const filterMerchants = () => {
    let filtered = merchants;

    // Category filter
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(merchant => merchant.category === selectedCategory);
    }

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(merchant =>
        merchant.business_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (merchant.email && merchant.email.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (merchant.mpesa_paybill && merchant.mpesa_paybill.includes(searchTerm))
      );
    }

    setFilteredMerchants(filtered);
    setCurrentPage(1);
  };

  const categories = ['all', 'Retail', 'Restaurant', 'Services', 'Entertainment', 'Transportation', 'Other'];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    try {
      await api.createMerchant(formData);
      setSuccess('Merchant created successfully!');
      setShowModal(false);
      setFormData({ business_name: '', category: '', mpesa_paybill: '', email: '' });
      loadMerchants();
      onUpdate();
    } catch (err: any) {
      setError(err.response?.data?.error || 'Operation failed');
    }
  };

  const openNewModal = () => {
    setFormData({ business_name: '', category: '', mpesa_paybill: '', email: '' });
    setShowModal(true);
  };

  if (loading) {
    return <div className="loading">Loading merchants...</div>;
  }

  // Pagination
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentMerchants = filteredMerchants.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(filteredMerchants.length / itemsPerPage);

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>Merchants</h1>
          <p className="page-subtitle">Manage merchant accounts and payment details ({filteredMerchants.length} total)</p>
        </div>
        <button className="btn btn-primary" onClick={openNewModal}>
          Add Merchant
        </button>
      </div>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      <div className="card">
        <div className="table-controls">
          <div className="search-box">
            <input
              type="text"
              placeholder="Search by business name, email, or paybill..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>
          <div className="filter-tags">
            {categories.map(category => (
              <button
                key={category}
                className={`filter-tag ${selectedCategory === category ? 'active' : ''}`}
                onClick={() => setSelectedCategory(category)}
              >
                {category === 'all' ? 'All Categories' : category}
              </button>
            ))}
          </div>
        </div>

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Business Name</th>
                <th>Category</th>
                <th>M-PESA Paybill</th>
                <th>Email</th>
                <th>Total Transactions</th>
              </tr>
            </thead>
            <tbody>
              {currentMerchants.map((merchant) => (
                <tr key={merchant.id}>
                  <td>{merchant.id}</td>
                  <td>{merchant.business_name}</td>
                  <td>
                    <span className="badge">{merchant.category || '-'}</span>
                  </td>
                  <td>{merchant.mpesa_paybill || '-'}</td>
                  <td>{merchant.email || '-'}</td>
                  <td>KES {parseFloat(String(merchant.total_transactions || 0)).toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredMerchants.length === 0 && (
          <div className="empty-state">
            <p>{searchTerm || selectedCategory !== 'all' ? 'No merchants match your filters.' : 'No merchants found. Add your first merchant!'}</p>
          </div>
        )}

        {filteredMerchants.length > itemsPerPage && (
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
            <h2>Add New Merchant</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Business Name *</label>
                <input
                  type="text"
                  value={formData.business_name}
                  onChange={(e) => setFormData({ ...formData, business_name: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Category</label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                >
                  <option value="">Select category</option>
                  <option value="Retail">Retail</option>
                  <option value="Restaurant">Restaurant</option>
                  <option value="Services">Services</option>
                  <option value="Entertainment">Entertainment</option>
                  <option value="Transportation">Transportation</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <div className="form-group">
                <label>M-PESA Paybill</label>
                <input
                  type="text"
                  value={formData.mpesa_paybill}
                  onChange={(e) => setFormData({ ...formData, mpesa_paybill: e.target.value })}
                  placeholder="123456"
                />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="merchant@example.com"
                />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Merchants;

