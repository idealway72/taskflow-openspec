const Auth = {
  save(token, user) {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
  },
  getToken() { return localStorage.getItem('token'); },
  getUser() {
    const u = localStorage.getItem('user');
    return u ? JSON.parse(u) : null;
  },
  clear() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },
  requireAuth() {
    if (!this.getToken()) { location.href = '/login.html'; }
  },
  requireNoAuth() {
    if (this.getToken()) {
      const user = this.getUser();
      location.href = user?.team_id ? '/kanban.html' : '/team.html';
    }
  },
};
