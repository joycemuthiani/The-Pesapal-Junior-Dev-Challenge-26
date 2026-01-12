import axios, { AxiosResponse } from 'axios';
import { Customer, Merchant, Transaction, QueryResult, DatabaseStats } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Health check
  healthCheck: async (): Promise<{ status: string; database: string }> => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  // Query execution
  executeQuery: async (query: string): Promise<QueryResult> => {
    const response: AxiosResponse<QueryResult> = await apiClient.post('/query', { query });
    return response.data;
  },

  // Customers
  getCustomers: async (): Promise<Customer[]> => {
    const response = await apiClient.get('/customers');
    return response.data.customers;
  },

  getCustomer: async (id: number): Promise<Customer> => {
    const response: AxiosResponse<Customer> = await apiClient.get(`/customers/${id}`);
    return response.data;
  },

  createCustomer: async (customer: Omit<Customer, 'id'>): Promise<{ message: string; id: number }> => {
    const response = await apiClient.post('/customers', customer);
    return response.data;
  },

  updateCustomer: async (id: number, customer: Partial<Customer>): Promise<{ message: string }> => {
    const response = await apiClient.put(`/customers/${id}`, customer);
    return response.data;
  },

  deleteCustomer: async (id: number): Promise<{ message: string; soft_delete?: boolean; transaction_count?: number }> => {
    const response = await apiClient.delete(`/customers/${id}`);
    return response.data;
  },

  // Merchants
  getMerchants: async (): Promise<Merchant[]> => {
    const response = await apiClient.get('/merchants');
    return response.data.merchants;
  },

  createMerchant: async (merchant: Omit<Merchant, 'id' | 'total_transactions'>): Promise<{ message: string; id: number }> => {
    const response = await apiClient.post('/merchants', merchant);
    return response.data;
  },

  // Transactions
  getTransactions: async (): Promise<Transaction[]> => {
    const response = await apiClient.get('/transactions');
    return response.data.transactions;
  },

  createTransaction: async (transaction: Omit<Transaction, 'id' | 'name' | 'business_name'>): Promise<{ message: string; id: number }> => {
    const response = await apiClient.post('/transactions', transaction);
    return response.data;
  },

  // Stats
  getStats: async (): Promise<DatabaseStats> => {
    const response: AxiosResponse<DatabaseStats> = await apiClient.get('/stats');
    return response.data;
  },

  // Volume stats with period filter
  getVolumeStats: async (period: string): Promise<{ total_amount: number; status_breakdown: DatabaseStats['status_breakdown'] }> => {
    const response = await apiClient.get(`/stats/volume?period=${encodeURIComponent(period)}`);
    return response.data;
  },

  // Load test data
  loadTestData: async (): Promise<{ message: string; customers: number; merchants: number; transactions: number }> => {
    const response = await apiClient.post('/load-test-data');
    return response.data;
  },
};

