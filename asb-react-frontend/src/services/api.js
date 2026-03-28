import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE || (
    window.location.hostname.includes('asbreports.in')
        ? 'https://api.asbreports.in'
        : `http://${window.location.hostname}:8001`
);

const apiInstance = axios.create({
    baseURL: API_BASE,
    timeout: 180000, // 3 minutes — AI and heavy PDF calls need more time
});

const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return token ? { 'X-Auth-Token': token } : {};
};

export const api = {
    instance: apiInstance, // Expose for direct use (e.g. PDF with progress tracking)
    get: async (path, params = {}) => {
        try {
            const response = await apiInstance.get(path, {
                params,
                headers: getAuthHeaders()
            });
            return response.data;
        } catch (error) {
            console.error(`GET ${path} failed:`, error);
            throw error;
        }
    },
    post: async (path, data = {}) => {
        try {
            const response = await apiInstance.post(path, data, {
                headers: getAuthHeaders()
            });
            return response.data;
        } catch (error) {
            console.error(`POST ${path} failed:`, error);
            throw error;
        }
    },
    getBytes: async (path, params = {}) => {
        try {
            const response = await apiInstance.get(path, {
                params,
                headers: getAuthHeaders(),
                responseType: 'blob'
            });
            return response.data;
        } catch (error) {
            console.error(`GET ${path} (bytes) failed:`, error);
            throw error;
        }
    }
};

export default api;
