export const getToken = (): string | null => {
    if (typeof window !== 'undefined') {
        return localStorage.getItem('access_token');
    }
    return null;
};

export const setToken = (token: string) => {
    if (typeof window !== 'undefined') {
        localStorage.setItem('access_token', token);
    }
};

export const removeToken = () => {
    if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token');
    }
};

export const isAuthenticated = (): boolean => {
    return !!getToken();
};
