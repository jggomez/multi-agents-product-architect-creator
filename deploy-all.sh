#!/bin/bash
# ==============================================================================
# deploy-all.sh - Deploy all agents and frontend to GCP Cloud Run
# ==============================================================================
# This script deploys services in the correct order:
# 1. Sub-agents (analyst, architect, ux-designer, critic) - in parallel
# 2. Orchestrator (needs sub-agent URLs)
# 3. Frontend (needs orchestrator URL)
#
# Prerequisites:
# - gcloud CLI authenticated and configured
# - Artifact Registry repository created
# - Required APIs enabled (Cloud Run, Cloud Build, Artifact Registry)
#
# Usage:
#   ./deploy-all.sh <PROJECT_ID> <REGION>
#
# Example:
#   ./deploy-all.sh devhack-3f0c2 us-central1
# ==============================================================================

set -euo pipefail

PROJECT_ID="${1:?Usage: ./deploy-all.sh <PROJECT_ID> <REGION>}"
REGION="${2:-us-central1}"
REPO_NAME="agent-ux"
LOCATION="global"
LOGS_BUCKET="docs-agents-software"

echo "=============================================="
echo "  Multi-Agent UX System - Cloud Run Deployment"
echo "=============================================="
echo "Project:    ${PROJECT_ID}"
echo "Region:     ${REGION}"
echo "Repository: ${REPO_NAME}"
echo ""

# --- Step 0: Create Artifact Registry repository (if not exists) ---
echo "[0/6] Ensuring Artifact Registry repository exists..."
gcloud artifacts repositories describe "${REPO_NAME}" \
  --location="${REGION}" \
  --project="${PROJECT_ID}" 2>/dev/null || \
gcloud artifacts repositories create "${REPO_NAME}" \
  --repository-format=docker \
  --location="${REGION}" \
  --project="${PROJECT_ID}" \
  --description="Multi-Agent UX System container images"
echo ""

# --- Helper function ---
deploy_agent() {
  local SERVICE_NAME="$1"
  local SERVICE_DIR="$2"
  local EXTRA_SUBS="${3:-}"

  # Construct substitutions string
  local SUBS="_REGION=${REGION},_REPO_NAME=${REPO_NAME},_LOGS_BUCKET=${LOGS_BUCKET}"
  if [ -n "${EXTRA_SUBS}" ]; then
    SUBS="${SUBS},${EXTRA_SUBS}"
  fi

  echo "  Building and Deploying ${SERVICE_NAME} via Cloud Build..." >&2
  
  gcloud builds submit . \
    --config="${SERVICE_DIR}/cloudbuild.yaml" \
    --project="${PROJECT_ID}" \
    --substitutions="${SUBS}" >&2

  # Get the deployed URL
  local URL
  URL=$(gcloud run services describe "${SERVICE_NAME}" \
    --region="${REGION}" \
    --project="${PROJECT_ID}" \
    --format='value(status.url)')
  
  echo "  ${SERVICE_NAME} deployed at: ${URL}" >&2
  echo "${URL}"
}

# --- Step 1: Configure Docker for Artifact Registry ---
echo "[1/6] Configuring Docker authentication..."
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet
echo ""

# --- Step 2: Deploy sub-agents ---
echo "[2/6] Deploying sub-agents..."
echo ""

ANALYST_URL=$(deploy_agent "analyst" "agents/analyst")
echo ""
ARCHITECT_URL=$(deploy_agent "architect" "agents/architect")
echo ""
UX_DESIGNER_URL=$(deploy_agent "ux-designer" "agents/ux-designer" "_STITCH_API_KEY=${STITCH_API_KEY:-}")
echo ""
CRITIC_URL=$(deploy_agent "critic" "agents/critic" "_STITCH_API_KEY=${STITCH_API_KEY:-}")
echo ""

# Sub-agents deployed!
echo "[3/6] Sub-agents deployed successfully!"
echo "  Analyst:     ${ANALYST_URL}"
echo "  Architect:   ${ARCHITECT_URL}"
echo "  UX Designer: ${UX_DESIGNER_URL}"
echo "  Critic:      ${CRITIC_URL}"
echo ""

# --- Step 4: Deploy orchestrator ---
echo "[4/6] Deploying orchestrator..."
ORCH_SUBS="_ANALYST_URL=${ANALYST_URL},_ARCHITECT_URL=${ARCHITECT_URL},_UX_DESIGNER_URL=${UX_DESIGNER_URL},_CRITIC_URL=${CRITIC_URL},_MODEL_ARMOR_LOCATION=${REGION},_MODEL_ARMOR_TEMPLATE_ID=multi-agents-product-security"
ORCHESTRATOR_URL=$(deploy_agent "orchestrator" "agents/orchestrator" "${ORCH_SUBS}")
echo ""

echo "[5/6] Orchestrator deployed at: ${ORCHESTRATOR_URL}"
echo ""

# --- Step 5: Deploy frontend ---
echo "[6/6] Deploying frontend..."
FRONTEND_URL=$(deploy_agent "frontend" "frontend" "_ORCHESTRATOR_URL=${ORCHESTRATOR_URL}")

echo ""
echo "=============================================="
echo "  Deployment Complete!"
echo "=============================================="
echo ""
echo "Service URLs:"
echo "  Frontend (UI):  ${FRONTEND_URL}"
echo "  Orchestrator:   ${ORCHESTRATOR_URL}"
echo "  Analyst:        ${ANALYST_URL}"
echo "  Architect:      ${ARCHITECT_URL}"
echo "  UX Designer:    ${UX_DESIGNER_URL}"
echo "  Critic:         ${CRITIC_URL}"
echo ""
echo "All services: 1 CPU, 512Mi RAM, unauthenticated access"
echo "=============================================="
