/**
 * ==============================================================================
 * CLIENTE DE AUTENTICACIÓN JWT Y CONSUMO DE API REST
 * Institución Universitaria del Putumayo - UniPutumayo
 * ==============================================================================
 */

const Auth = {
  getAccessToken() {
    return localStorage.getItem('jwt_access_token') || localStorage.getItem('access_token');
  },

  getRefreshToken() {
    return localStorage.getItem('jwt_refresh_token') || localStorage.getItem('refresh_token');
  },

  getUser() {
    const u = localStorage.getItem('jwt_user');
    try {
      return u ? JSON.parse(u) : null;
    } catch (e) {
      return null;
    }
  },

  setSession(accessToken, refreshToken, user) {
    if (accessToken) localStorage.setItem('jwt_access_token', accessToken);
    if (refreshToken) localStorage.setItem('jwt_refresh_token', refreshToken);
    if (user) localStorage.setItem('jwt_user', JSON.stringify(user));
  },

  clearSession() {
    localStorage.removeItem('jwt_access_token');
    localStorage.removeItem('jwt_refresh_token');
    localStorage.removeItem('jwt_user');
  },

  isAuthenticated() {
    return !!this.getAccessToken();
  },

  hasPermission(permCode) {
    const user = this.getUser();
    if (!user) return false;
    if (user.is_superuser) return true;
    const perms = user.permisos || [];
    return perms.includes(permCode);
  },

  async login(username, password) {
    const response = await fetch('/api/auth/login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });

    const data = await response.json();
    if (!response.ok) {
      const msg = data.detail || (data.non_field_errors ? data.non_field_errors[0] : 'Credenciales inválidas o cuenta desactivada.');
      throw new Error(msg);
    }

    this.setSession(data.access, data.refresh, data.user);
    return data;
  },

  async logout() {
    try {
      if (this.isAuthenticated()) {
        await this.apiFetch('/api/auth/logout/', { method: 'POST' });
      }
    } catch (e) {
      console.warn('Logout server notification failed', e);
    } finally {
      this.clearSession();
      window.location.href = '/';
    }
  },

  async refreshToken() {
    const refresh = this.getRefreshToken();
    if (!refresh) throw new Error('No refresh token available');

    const response = await fetch('/api/auth/token/refresh/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh })
    });

    if (!response.ok) {
      this.clearSession();
      window.location.href = '/';
      throw new Error('Sesión expirada');
    }

    const data = await response.json();
    localStorage.setItem('jwt_access_token', data.access);
    return data.access;
  },

  async apiFetch(url, options = {}) {
    let token = this.getAccessToken();
    const headers = options.headers ? { ...options.headers } : {};

    if (!(options.body instanceof FormData)) {
      if (!headers['Content-Type']) {
        headers['Content-Type'] = 'application/json';
      }
    }

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    options.headers = headers;

    let response = await fetch(url, options);

    // Si el token expiró, intentar renovar transparentemente (Sec 2.1)
    if (response.status === 401 && this.getRefreshToken()) {
      try {
        const newToken = await this.refreshToken();
        headers['Authorization'] = `Bearer ${newToken}`;
        options.headers = headers;
        response = await fetch(url, options);
      } catch (err) {
        this.clearSession();
        window.location.href = '/';
        throw err;
      }
    }

    return response;
  },

  requireAuth(redirectUrl = '/') {
    if (!this.isAuthenticated()) {
      window.location.href = redirectUrl;
    }
  },

  requireAdmin(redirectUrl = '/estudiante/') {
    const user = this.getUser();
    if (!user || (!user.is_superuser && user.rol?.nombre !== 'Administrador')) {
      window.location.href = redirectUrl;
    }
  }
};

// Exponer Auth y authFetch globalmente para compatibilidad total
window.Auth = Auth;
window.authFetch = function(url, options) {
  return Auth.apiFetch(url, options);
};
