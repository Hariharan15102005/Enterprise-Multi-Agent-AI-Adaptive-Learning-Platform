import apiClient from './client';

export const dashboardApi = {
  getKPIs: (params = {}) => apiClient.get('/api/v1/dashboard/kpis', params),
  getSummary: (params = {}) => apiClient.get('/api/v1/dashboard/summary', params),
};

export const analyticsApi = {
  getRevenueTrends: (params = { interval: 'month' }) => apiClient.get('/api/v1/analytics/revenue', params),
  getCategoryAnalytics: (params = { limit: 10, sort_by: 'gmv' }) => apiClient.get('/api/v1/analytics/categories', params),
  getPaymentAnalytics: () => apiClient.get('/api/v1/analytics/payments'),
  getInsights: () => apiClient.get('/api/v1/analytics/insights'),
};

export const customersApi = {
  getSegments: () => apiClient.get('/api/v1/customers/segments'),
  getGeoDistribution: () => apiClient.get('/api/v1/customers/geo'),
  getCustomersList: (params = { page: 1, page_size: 20 }) => apiClient.get('/api/v1/customers/list', params),
};
