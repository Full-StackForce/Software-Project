(function () {
  const API_BASE = "http://localhost:8000";

  const storage = {
    get(key, fallbackValue = null) {
      const value = localStorage.getItem(key);
      return value === null ? fallbackValue : value;
    },
    set(key, value) {
      localStorage.setItem(key, String(value));
    },
    remove(key) {
      localStorage.removeItem(key);
    },
    removeMany(keys) {
      for (const key of keys) {
        localStorage.removeItem(key);
      }
    },
  };

  const sessionKeys = {
    userId: "userId",
    userName: "userName",
    userEmail: "userEmail",
    userStreak: "userStreak",
  };

  const session = {
    keys: sessionKeys,
    getUserId() {
      const raw = storage.get(sessionKeys.userId, "");
      const parsed = Number(raw);
      return Number.isFinite(parsed) && parsed > 0 ? parsed : null;
    },
    requireUser(redirectPath) {
      const userId = this.getUserId();
      if (!userId) {
        window.location.href = redirectPath;
        return null;
      }
      return userId;
    },
  };

  window.PulseApp = {
    API_BASE,
    storage,
    session,
  };
})();
