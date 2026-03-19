// API Configuration
// This file detects whether we're running locally or in production

const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

const config = {
    apiUrl: isLocalhost
        ? 'http://localhost:7071/api'  // Local Azure Functions
        : 'https://surgical-outcomes-api.azurewebsites.net/api',  // Production - update with your actual URL

    // Helper function to make authenticated API calls
    async apiCall(endpoint, options = {}) {
        const token = localStorage.getItem('authToken');
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(`${this.apiUrl}/${endpoint}`, {
            ...options,
            headers
        });

        if (response.status === 401) {
            // Token expired or invalid
            localStorage.removeItem('authToken');
            localStorage.removeItem('user');
            window.location.href = '/login.html';
            throw new Error('Authentication required');
        }

        return response;
    },

    // Get current user from localStorage
    getCurrentUser() {
        const userJson = localStorage.getItem('user');
        return userJson ? JSON.parse(userJson) : null;
    },

    // Check if user is logged in
    isAuthenticated() {
        return !!localStorage.getItem('authToken');
    },

    // Logout
    logout() {
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
        window.location.href = '/login.html';
    }
};

// Make config globally available
window.appConfig = config;
