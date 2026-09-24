import apiClient from './client';

export const productsApi = {
  getProductsList: (params = { page: 1, page_size: 20, sort_by: 'items_sold' }) =>
    apiClient.get('/api/v1/products/list', params),
};

export const sellersApi = {
  getLeaderboard: (params = { limit: 20, sort_by: 'sales' }) =>
    apiClient.get('/api/v1/sellers/leaderboard', params),
};

export const logisticsApi = {
  getOverview: () => apiClient.get('/api/v1/logistics/overview'),
  getByState: () => apiClient.get('/api/v1/logistics/by-state'),
};

export const dataQualityApi = {
  getOverview: () => apiClient.get('/api/v1/data-quality/overview'),
};

export const mlApi = {
  getModels: () => apiClient.get('/api/v1/ml/models'),
  getModelDetails: (modelName) => apiClient.get(`/api/v1/ml/models/${modelName}`),
  getSegments: () => apiClient.get('/api/v1/ml/segments'),
  getCustomerSegment: (customerUniqueId) => apiClient.get(`/api/v1/ml/customers/${customerUniqueId}/segment`),
  predictDeliveryRisk: (payload) => apiClient.post('/api/v1/ml/delivery-risk/predict', payload),
  getOrderDeliveryRisk: (orderId) => apiClient.get(`/api/v1/ml/delivery-risk/${orderId}`),
  getOrderSatisfactionRisk: (orderId) => apiClient.get(`/api/v1/ml/satisfaction-risk/${orderId}`),
  getForecast: (params = { target: 'daily_gmv', horizon_days: 30 }) => apiClient.get('/api/v1/ml/forecast', params),
  getAnomalies: (params = { limit: 50 }) => apiClient.get('/api/v1/ml/anomalies', params),
};

export const aiApi = {
  query: (question, conversationContext = []) =>
    apiClient.post('/api/v1/ai/query', { question, conversation_context: conversationContext }),
  getHealth: () => apiClient.get('/api/v1/ai/health'),
  getCapabilities: () => apiClient.get('/api/v1/ai/capabilities'),
};

export const systemApi = {
  getHealth: () => apiClient.get('/health'),
};
