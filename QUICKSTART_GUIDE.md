# 🚀 Cloud Run Hackathon - Quick Start Guide

**Get your AI agent running in 30 minutes!**

## ⚡ Prerequisites (5 minutes)

```bash
# 1. Install Google Cloud SDK (if not already installed)
curl https://sdk.cloud.google.com | bash

# 2. Authenticate and set project
gcloud auth login
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID
gcloud config set run/region europe-west1

# 3. Enable required APIs
gcloud services enable run.googleapis.com cloudbuild.googleapis.com aiplatform.googleapis.com
```

## 🤖 Deploy A Pre-Built Gemma LLM Container (10-15 minutes)

```bash
# Deploy Gemma 3-4B directly to Cloud Run with one command (secure by default)
gcloud run deploy SERVICE_NAME \
    --image us-docker.pkg.dev/cloudrun/container/gemma/GEMMA_PARAMETER \
    --concurrency 4 \
    --cpu 8 \
    --gpu 1 \
    --gpu-type nvidia-l4 \
    --max-instances 1 \
    --memory 32Gi \
    --allow-unauthenticated \
    --no-cpu-throttling \
    --timeout=600 \
    --region REGION \
    --no-gpu-zonal-redundancy \
    --labels dev-tutorial=hackathon-nyc-cloud-run-gpu-25

# SERVICE_NAME = anything-you-want
# GEMMA_PARAMETER = gemma3-4b
# REGION = europe-west1

# Get your Gemma URL
export GEMMA_URL=$(gcloud run services describe SERVICE_NAME --format='value(status.url)')
echo "🎉 Gemma deployed at: $GEMMA_URL"
```

💡 **Want to explore other Gemma deployment options?** Here are all the supported models, so far:

```
us-docker.pkg.dev/cloudrun/container/gemma/gemma3-1b
us-docker.pkg.dev/cloudrun/container/gemma/gemma3-4b
us-docker.pkg.dev/cloudrun/container/gemma/gemma3-12b
us-docker.pkg.dev/cloudrun/container/gemma/gemma3-27b
us-docker.pkg.dev/cloudrun/container/gemma/gemma3n-e2b
us-docker.pkg.dev/cloudrun/container/gemma/gemma3n-e4b
```

Note, When testing the endpoint, you should use the following `model: "gemma-string"` when interacting with the deployed Gemma service:


```
gemma3-1b = gemma3:1b
gemma3-4b = gemma3:4b
gemma3-12b = gemma3:12b
gemma3-27b = gemma3:27b
gemma3n-e2b = gemma3n:e2b
gemma3n-e4b = gemma3n:e4b
```


## 🧪 Test Gemma Service (5 minutes)

Before deploying the hackathon agent, let's test the Gemma service to make sure it's working:

```bash
# Start the proxy (choose Y when prompted to install cloud-run-proxy component)
gcloud run services proxy SERVICE_NAME --port=9090
```

In a separate terminal tab, test the service:

```bash
# Send a request to test the Gemma service
curl http://localhost:9090/api/generate -d '{
  "model": "gemma3:4b",
  "prompt": "Why is the sky blue?"
}'
```

If you get a response, your Gemma service is working correctly! Keep the proxy running and continue in the original terminal.

## 🛠️ Deploy Your Agent (10 minutes)

```bash
# 1. Clone the hackathon repository
git clone https://github.com/amitkmaraj/cloud-run-hackathon-2025.git
cd cloud-run-hackathon-2025/hackathon-agent

# 2. Create .env file with your configuration
cat > .env << EOF
GEMMA_URL=$GEMMA_URL
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=TRUE
EOF

echo "⚠️  Please edit .env file and update the following values:"
echo "   - GOOGLE_CLOUD_PROJECT: Set to your actual project ID"
echo "   - GEMMA_URL: Already set to $GEMMA_URL"

# 3. Export environment variables from .env file
cd hackathon-agent
export $(cat .env | xargs)

# 4. Deploy to Cloud Run (secure by default)
gcloud run deploy hackathon-agent \
    --source . \
    --region europe-west1 \
    --allow-unauthenticated \
    --memory=4Gi \
    --set-env-vars GEMMA_URL=$GEMMA_URL \
    --set-env-vars GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT \
    --set-env-vars GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION \
    --set-env-vars GOOGLE_GENAI_USE_VERTEXAI=$GOOGLE_GENAI_USE_VERTEXAI

# 5. Get your agent URL
export AGENT_URL=$(gcloud run services describe hackathon-agent --region=REGION --format='value(status.url)')
echo "🎉 Agent deployed at: $AGENT_URL"
```

## 🧪 Test Your Agent (5 minutes)

Now let's test your hackathon agent:

```bash
# Start the proxy for your agent
gcloud run services proxy hackathon-agent --port=8080
```

In a separate terminal tab, you can now access your agent through ADK web interface:

```bash
# Open your agent in the browser
echo "🌐 Open your agent at: http://localhost:8080"
```

## 🔐 Authentication Notes

Your services are deployed securely (recommended) with authentication required. The proxy commands automatically handle authentication for local testing.

For production use or direct API calls, you'll need to include authentication tokens:

```bash
# Get an authentication token
TOKEN=$(gcloud auth print-identity-token)

# Use in direct API calls
curl -H "Authorization: Bearer ${TOKEN}" \
  -X POST "${AGENT_URL}/api/tools/ask_gemma" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is serverless computing?",
    "context": "Im building a web application"
  }'
```

## 🎯 Next Steps

1. **Customize your agent** - Edit `agent.py` to add your own tools
2. **Test locally** - Set environment variables and run `uv run python server.py`
3. **Add features** - Extend with new capabilities for your domain
4. **Build something amazing!** 🚀

## 🆘 Need Help?

- Check that your .env file has the correct values
- Make sure both proxy commands are running in separate terminals
- Visit `http://localhost:8080/docs` to see your agent's API documentation when the proxy is running
- Ask mentors for help with deployment issues

**Ready to hack!** 🎉
