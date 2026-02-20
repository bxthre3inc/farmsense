
const API_BASE_URL = 'http://localhost:8000/api/v1';

export const getApiKey = () => localStorage.getItem('farmsense_investor_key');
export const setApiKey = (key: string) => localStorage.setItem('farmsense_investor_key', key);
export const removeApiKey = () => localStorage.removeItem('farmsense_investor_key');

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
    getFields: () => request('/fields'),
    getMetrics: () => request('/admin/metrics'),
    investorBuyIn: (amount: number) => request('/investor/buy-in', {
        method: 'POST',
        body: JSON.stringify({ amount }),
    }),
    getForecast: (fieldId: string) => request(`/fields/${fieldId}/forecast`),
};
