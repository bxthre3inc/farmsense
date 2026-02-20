
const API_BASE_URL = 'http://localhost:8000/api/v1';

export const getApiKey = () => localStorage.getItem('farmsense_grant_key');
export const setApiKey = (key: string) => localStorage.setItem('farmsense_grant_key', key);
export const removeApiKey = () => localStorage.removeItem('farmsense_grant_key');

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
    getGrantImpact: (grantId: string) => request(`/grants/${grantId}/impact`),
    getComplianceReports: (fieldId?: string) => request(`/compliance/reports${fieldId ? `?field_id=${fieldId}` : ''}`),

    // Support Letters
    getSupportLetters: (grantId: string) => request(`/grants/${grantId}/letters`),
    requestSupportLetter: (grantId: string, data: any) => request(`/grants/${grantId}/letters`, {
        method: 'POST',
        body: JSON.stringify(data)
    }),
    signSupportLetter: (letterId: string, signature: string) => request(`/letters/${letterId}/sign`, {
        method: 'POST',
        body: JSON.stringify({ signature_data: signature })
    }),
    verifySupportLetter: (letterId: string) => request(`/letters/${letterId}/verify`, {
        method: 'POST'
    }),
};
