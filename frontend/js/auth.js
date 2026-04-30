/* auth.js – Authentication logic */

const auth = {
  /**
   * Check if the current session is authenticated.
   * Redirects to login.html if not logged in (unless already on login page).
   */
  async checkAuth() {
    if (window.location.pathname.includes('login')) return;
    const res = await api.get('/api/auth/status');
    if (!res || !res.success || !res.data.logged_in) {
      window.location.href = '/login.html';
    }
  },

  /**
   * Attempt to log in with username and password.
   * Returns the API response object.
   */
  async login(username, password) {
    return api.post('/api/auth/login', { username, password });
  },

  /**
   * Log out the current session and redirect to login page.
   */
  async logout() {
    await api.post('/api/auth/logout');
    window.location.href = '/login.html';
  },

  /**
   * Get current auth status.
   * Returns { logged_in: bool, username: string } on success.
   */
  async status() {
    const res = await api.get('/api/auth/status');
    return (res && res.success) ? res.data : { logged_in: false };
  }
};
