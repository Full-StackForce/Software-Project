(function () {
  const API_BASE = window.location.origin;
  // Remove the password draft saved by older versions. Never restore it.
  localStorage.removeItem("pulsePassword");

  const storage = {
    get(key, fallbackValue = null) {
      const value = localStorage.getItem(key);
      return value === null ? fallbackValue : value;
    },
    set(key, value) { localStorage.setItem(key, String(value)); },
    remove(key) { localStorage.removeItem(key); },
    removeMany(keys) { keys.forEach(key => localStorage.removeItem(key)); },
  };
  const sessionKeys = {
    userId: "userId", userName: "userName", userEmail: "userEmail", userStreak: "userStreak",
  };
  async function apiFetch(input, options = {}) {
    const url = new URL(input, window.location.origin);
    if (url.origin !== window.location.origin) throw new Error("API requests must stay on this site.");
    const headers = new Headers(options.headers);
    const method = (options.method || "GET").toUpperCase();
    if (!["GET", "HEAD", "OPTIONS"].includes(method)) headers.set("X-PulsePoint-Request", "1");
    const response = await window.fetch(url, { ...options, headers, credentials: "same-origin", cache: "no-store" });
    if (response.status === 401 && !["/auth/login", "/auth/me", "/auth/logout"].includes(url.pathname)) {
      storage.removeMany(Object.values(sessionKeys));
      window.location.assign("/login");
    }
    return response;
  }
  const session = {
    keys: sessionKeys,
    async requireUser(redirectPath = "/login") {
      try {
        const response = await apiFetch("/auth/me");
        if (!response.ok) throw new Error("Please sign in.");
        const user = await response.json();
        // Display cache only. Authentication is exclusively the HttpOnly cookie.
        storage.set(sessionKeys.userId, user.user_id);
        storage.set(sessionKeys.userName, user.name || "");
        storage.set(sessionKeys.userEmail, user.email || "");
        storage.set(sessionKeys.userStreak, user.current_streak || 0);
        return user.user_id;
      } catch {
        storage.removeMany(Object.values(sessionKeys));
        window.location.assign(redirectPath);
        return null;
      }
    },
    async logout() {
      const response = await apiFetch("/auth/logout", { method: "POST" });
      if (!response.ok) throw new Error("Could not sign out. Please try again.");
      storage.removeMany(Object.values(sessionKeys));
      window.location.assign("/login");
    },
  };
  window.PulseApp = { API_BASE, storage, session, apiFetch };
})();
