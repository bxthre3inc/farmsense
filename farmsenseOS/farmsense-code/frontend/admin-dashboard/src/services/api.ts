
const API_BASE_URL = 'http://localhost:8000/api/v1';

export const getApiKey = () => localStorage.getItem('farmsense_admin_key');
export const setApiKey = (key: string) => localStorage.setItem('farmsense_admin_key', key);
export const removeApiKey = () => localStorage.removeItem('farmsense_admin_key');

async function request(endpoint: string, options: RequestInit = {}) {
    const apiKey = getApiKey();
    const headers = {
        'Content-Type': 'application/json',
        'X-API-Key': apiKey || '',
        ...options.headers,
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });

    if (!response.ok) {
        if (response.status === 403) {
            removeApiKey();
            window.location.reload();
        }
        const error = await response.json();
        throw new Error(error.detail || 'API request failed');
    }

    return response.json();
}

export const api = {
    getUsers: () => request('/admin/users'),
    createUser: (userData: any) => request('/admin/users', {
        method: 'POST',
        body: JSON.stringify(userData),
    }),
    updateUser: (userId: string, updateData: any) => request(`/admin/users/${userId}`, {
        method: 'PUT',
        body: JSON.stringify(updateData),
    }),
    getFields: () => request('/fields'),
    getMetrics: () => request('/admin/metrics'),
    signLetter: (token: string, signature: string) => request(`/letters/${token}/sign`, {
        method: 'POST',
        body: JSON.stringify({ signature_data: signature }),
    }),
};
