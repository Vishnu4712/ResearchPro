#!/bin/bash

# ResearchPro Deployment Script for Vertex AI Agent Engine
# This script automates the deployment process

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"
REGION="${VERTEX_LOCATION:-us-central1}"
AGENT_NAME="researchpro-agent"
AGENT_VERSION="1.0.0"

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}ResearchPro Agent Deployment${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI not found. Please install it first.${NC}"
    exit 1
fi

# Check if adk is installed
if ! command -v adk &> /dev/null; then
    echo -e "${YELLOW}ADK CLI not found. Installing...${NC}"
    pip install google-adk
fi

# Verify GCP project
echo "Using GCP Project: $PROJECT_ID"
echo "Using Region: $REGION"
echo ""

# Step 1: Enable required APIs
echo -e "${YELLOW}Step 1: Enabling required Google Cloud APIs...${NC}"
gcloud services enable aiplatform.googleapis.com --project=$PROJECT_ID
gcloud services enable generativelanguage.googleapis.com --project=$PROJECT_ID
gcloud services enable cloudresourcemanager.googleapis.com --project=$PROJECT_ID
echo -e "${GREEN}✓ APIs enabled${NC}"
echo ""

# Step 2: Create service account (if doesn't exist)
echo -e "${YELLOW}Step 2: Setting up service account...${NC}"
SA_NAME="researchpro-agent-sa"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

if ! gcloud iam service-accounts describe $SA_EMAIL --project=$PROJECT_ID &> /dev/null; then
    gcloud iam service-accounts create $SA_NAME \
        --display-name="ResearchPro Agent Service Account" \
        --project=$PROJECT_ID
    
    # Grant necessary roles
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="roles/aiplatform.user"
    
    echo -e "${GREEN}✓ Service account created${NC}"
else
    echo -e "${GREEN}✓ Service account already exists${NC}"
fi
echo ""

# Step 3: Create Vertex AI Memory Bank (optional)
echo -e "${YELLOW}Step 3: Setting up Vertex AI Memory Bank...${NC}"
read -p "Create new Memory Bank? (y/n): " create_memory
if [ "$create_memory" = "y" ]; then
    MEMORY_BANK_NAME="researchpro-memory"
    
    # Create memory bank using gcloud
    # Note: Adjust command based on latest gcloud syntax
    echo "Creating memory bank: $MEMORY_BANK_NAME"
    # gcloud ai memory-banks create $MEMORY_BANK_NAME \
    #     --region=$REGION \
    #     --project=$PROJECT_ID
    
    echo -e "${YELLOW}Note: Memory Bank creation may require manual setup via Console${NC}"
fi
echo ""

# Step 4: Store secrets
echo -e "${YELLOW}Step 4: Setting up secrets in Secret Manager...${NC}"
if [ -z "$GOOGLE_API_KEY" ]; then
    read -p "Enter your Gemini API Key: " GOOGLE_API_KEY
fi

# Create secret for API key
echo -n "$GOOGLE_API_KEY" | gcloud secrets create gemini-api-key \
    --data-file=- \
    --replication-policy="automatic" \
    --project=$PROJECT_ID 2>/dev/null || \
echo "Secret gemini-api-key already exists"

# Grant secret access to service account
gcloud secrets add-iam-policy-binding gemini-api-key \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/secretmanager.secretAccessor" \
    --project=$PROJECT_ID

echo -e "${GREEN}✓ Secrets configured${NC}"
echo ""

# Step 5: Build and deploy agent
echo -e "${YELLOW}Step 5: Building and deploying agent...${NC}"

# Navigate to project root
cd "$(dirname "$0")/.."

# Deploy using ADK CLI
adk deploy \
    --agent-path research_pro/main.py \
    --agent-class ResearchProSystem \
    --region $REGION \
    --project $PROJECT_ID \
    --service-account $SA_EMAIL \
    --config deployment/agent_config.yaml

echo -e "${GREEN}✓ Agent deployed successfully!${NC}"
echo ""

# Step 6: Test deployment
echo -e "${YELLOW}Step 6: Testing deployment...${NC}"

# Get agent endpoint
AGENT_ENDPOINT=$(gcloud run services describe $AGENT_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format='value(status.url)' 2>/dev/null || echo "")

if [ -n "$AGENT_ENDPOINT" ]; then
    echo "Agent endpoint: $AGENT_ENDPOINT"
    
    # Test health check
    echo "Testing health endpoint..."
    curl -s "${AGENT_ENDPOINT}/health" || echo "Health check not available yet"
else
    echo "Endpoint not ready yet. Check Cloud Console for status."
fi

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "Next steps:"
echo "1. View your agent in Cloud Console:"
echo "   https://console.cloud.google.com/vertex-ai/agents"
echo ""
echo "2. Monitor logs:"
echo "   gcloud logging read 'resource.type=cloud_run_revision' --project=$PROJECT_ID --limit=50"
echo ""
echo "3. Test the agent:"
echo "   python test_deployed_agent.py"
echo ""
echo "4. View metrics:"
echo "   https://console.cloud.google.com/monitoring"
echo ""

# Save deployment info
cat > deployment_info.txt << EOF
ResearchPro Agent Deployment Info
=================================
Date: $(date)
Project ID: $PROJECT_ID
Region: $REGION
Agent Name: $AGENT_NAME
Service Account: $SA_EMAIL
Endpoint: $AGENT_ENDPOINT

To redeploy:
  ./deployment/deploy.sh

To test:
  python test_deployed_agent.py
  
To view logs:
  gcloud logging read 'resource.type=cloud_run_revision' --project=$PROJECT_ID
  
To delete:
  gcloud run services delete $AGENT_NAME --region=$REGION --project=$PROJECT_ID
EOF

echo -e "${GREEN}Deployment info saved to deployment_info.txt${NC}"
