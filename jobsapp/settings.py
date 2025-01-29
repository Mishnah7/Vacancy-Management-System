# Session Settings
SESSION_COOKIE_AGE = 28800  # 8 hours in seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_SECURE = True  # Only send cookie over HTTPS
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
SESSION_COOKIE_SAMESITE = 'Lax'  # Provides CSRF protection

# Security Settings
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_USE_SESSIONS = True

# Idle timeout (optional but recommended)
SESSION_IDLE_TIMEOUT = 1800  # 30 minutes in seconds

# ... existing code ... 