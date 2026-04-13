/* api.js – re-exported for standalone import if needed */
// The main api object is defined in main.js.
// This file exists so api.js can be imported independently in other contexts.
if (typeof window !== 'undefined' && !window.api) {
  window.API_URL = window.API_URL || 'http://localhost:5000';

  window.api = {
    async request(method, path, data = null, formData = null) {
      const opts = { method, credentials: 'include', headers: {} };
      if (formData) {
        opts.body = formData;
      } else if (data) {
        opts.headers['Content-Type'] = 'application/json';
        opts.body = JSON.stringify(data);
      }
      try {
        const res = await fetch(window.API_URL + path, opts);
        if (res.status === 401) { window.location.href = '/login.html'; return null; }
        return await res.json();
      } catch (err) {
        return { success: false, error: 'Error de conexión' };
      }
    },
    get:    (path)       => window.api.request('GET',    path),
    post:   (path, data) => window.api.request('POST',   path, data),
    put:    (path, data) => window.api.request('PUT',    path, data),
    delete: (path)       => window.api.request('DELETE', path),
    upload: (path, fd)   => window.api.request('POST',   path, null, fd),
  };
}
