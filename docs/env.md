Environment Variables
=====================

Var | Default | Description
----|---------|----
DEBUG | "True" | Django DEBUG mode
APP_LOG_LEVEL | "ERROR" | Log level for application
GOOGLE_ANALYTICS_ID | "0" | Google Analytics ID
VK_ACCESS_TOKEN | "-" | [VK access token](get_vk_access_token.md) for VK API (It needs for test)
DJANGO_SECRET_KEY | "change_it" | [Django SECRET_KEY](https://docs.djangoproject.com/en/3.0/ref/settings/#std:setting-SECRET_KEY)
DATABASE_URL | None | Database URL
REDIS_URL | "redis://localhost:6379" | Redis URL
SENTRY_BACKEND_DSN | "" | Sentry DSN for backend
SENTRY_FRONTEND_DSN | undefined | Sentry DSN for frontend (Only for frontend build, locate in `.env.production.local`)
