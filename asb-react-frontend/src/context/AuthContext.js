import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [loading, setLoading] = useState(true);

    const API_BASE = process.env.REACT_APP_API_BASE || `http://${window.location.hostname}:8001`;

    const handleSSO = React.useCallback(async (ssoToken) => {
        setLoading(true);
        try {
            const response = await axios.get(`${API_BASE}/api/auth/me`, {
                headers: { 'X-Auth-Token': ssoToken }
            });
            if (response.data.success) {
                setToken(ssoToken);
                setUser(response.data.user);
                localStorage.setItem('token', ssoToken);

                // Clear query params to clean URL
                const newUrl = window.location.origin + window.location.pathname;
                window.history.replaceState({}, document.title, newUrl);
            }
        } catch (error) {
            console.error("SSO Token validation failed:", error);
        } finally {
            setLoading(false);
        }
    }, [API_BASE]);

    const fetchUser = React.useCallback(async () => {
        try {
            const response = await axios.get(`${API_BASE}/api/auth/me`, {
                headers: { 'X-Auth-Token': token }
            });
            if (response.data.success) {
                setUser(response.data.user);
            } else {
                localStorage.removeItem('token');
                setToken(null);
                setUser(null);
            }
        } catch (err) {
            console.error("Failed to fetch user:", err);
            localStorage.removeItem('token');
            setToken(null);
            setUser(null);
        } finally {
            setLoading(false);
        }
    }, [token, API_BASE]);

    useEffect(() => {
        // 1. Check URL for SSO Token (Single Sign-On from asbcrystal.in)
        const params = new URLSearchParams(window.location.search);
        const ssoToken = params.get('sso_token') || params.get('token');

        if (ssoToken && ssoToken !== token) {
            handleSSO(ssoToken);
        } else if (token) {
            localStorage.setItem('token', token);
            fetchUser();
        } else {
            localStorage.removeItem('token');
            setUser(null);
            setLoading(false);
        }
    }, [token, API_BASE, handleSSO, fetchUser]);

    const login = (newToken, userData) => {
        setToken(newToken);
        setUser(userData);
    };

    const logout = () => {
        setToken(null);
        setUser(null);
        localStorage.removeItem('token');
        localStorage.removeItem('pending_dob');
        localStorage.removeItem('pending_name');
    };

    const value = {
        user,
        token,
        loading,
        login,
        logout,
        fetchUser,
        API_BASE
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};
