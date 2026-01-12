/**
 * Type definitions for PyRelDB application
 */

export interface Customer {
  id: number;
  name: string;
  email: string;
  phone?: string;
  balance: number;
  created_at?: string;
}

export interface Merchant {
  id: number;
  business_name: string;
  category?: string;
  mpesa_paybill?: string;
  email?: string;
  total_transactions: number;
}

export interface Transaction {
  id: number;
  customer_id: number;
  merchant_id: number;
  amount: number;
  payment_method: string;
  status: string;
  transaction_date?: string;
  date_added?: string;
  added_by?: string;
  source?: string;
  // From JOIN queries
  name?: string;
  business_name?: string;
}

export interface QueryResult {
  columns: string[];
  rows: Record<string, any>[];
  message?: string;
  row_count: number;
}

export interface DatabaseStats {
  total_customers: number;
  total_merchants: number;
  total_transactions: number;
  total_amount: number;
  status_breakdown: {
    completed: { count: number; amount: number };
    pending: { count: number; amount: number };
    failed: { count: number; amount: number };
  };
  db_stats: {
    name: string;
    num_tables: number;
    tables: Record<string, TableStats>;
  };
}

export interface TableStats {
  columns: number;
  rows: number;
  indexes: number;
  size_kb: number;
}

export interface ApiError {
  error: string;
}

