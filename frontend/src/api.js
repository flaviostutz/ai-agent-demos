import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const loanAPI = {
  /**
   * Submit a loan application
   * @param {Object} loanData - The loan application data
   * @returns {Promise} - The API response
   */
  async submitApplication(loanData) {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/v1/loan/evaluate`,
        loanData,
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to submit application');
      }
      throw new Error('Network error. Please check if the API server is running.');
    }
  },

  /**
   * Check API health
   * @returns {Promise} - The health status
   */
  async checkHealth() {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`);
      return response.data;
    } catch (error) {
      throw new Error('API health check failed');
    }
  },
};
