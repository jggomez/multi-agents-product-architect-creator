#!/bin/sh
set -e

# Inject ORCHESTRATOR_URL into config.js at runtime
# Default to empty string if not set
ORCHESTRATOR_URL="${ORCHESTRATOR_URL:-http://localhost:8005}"

cat > /usr/share/nginx/html/js/config.js << EOF
/**
 * Application Configuration
 * This file acts as a bridge for environment variables.
 * Auto-generated at container startup.
 */

window.APP_CONFIG = {
    // Orchestrator URL (injected from environment)
    ORCHESTRATOR_URL: '${ORCHESTRATOR_URL}',
};
EOF

echo "Config injected: ORCHESTRATOR_URL=${ORCHESTRATOR_URL}"

# Execute the CMD
exec "$@"
