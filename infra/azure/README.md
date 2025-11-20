# Azure OpenAI Infrastructure

This directory contains Terraform configuration for deploying Azure OpenAI resources required by the Agentic Support Copilot.

## 🏗️ Resources Created

- **Resource Group**: Container for all Azure resources
- **Azure OpenAI Service**: Main AI service endpoint
- **GPT-4 Deployment**: Chat completion model for response generation
- **Text Embedding Deployment**: Vector embeddings for knowledge retrieval
- **API Keys**: Authentication credentials for the services

## 📋 Prerequisites

1. **Azure CLI**: Install from [Microsoft docs](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
2. **Terraform**: Install from [HashiCorp](https://developer.hashicorp.com/terraform/downloads)
3. **Azure Subscription**: Active subscription with Azure OpenAI access

## 🚀 Quick Start

### 1. Deploy Infrastructure

```bash
cd infra/azure
chmod +x deploy.sh
./deploy.sh
```

### 2. Configure Application

Copy the generated environment variables to your backend:

```bash
# Copy from generated azure.env to your .env
cp azure.env ../../apps/api/.env
```

### 3. Update Supabase Credentials

Edit `../../apps/api/.env` and add your Supabase credentials:

```env
# Azure OpenAI (auto-generated)
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_API_KEY=...

# Supabase (add manually)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### 4. Start Applications

```bash
# Backend
cd ../../apps/api
source .venv/bin/activate
uvicorn src.main:app --reload

# Frontend (new terminal)
cd ../../apps/web
npm run dev
```

## 📁 File Structure

```
infra/azure/
├── main.tf          # Main Terraform configuration
├── variables.tf     # Customizable variables
├── outputs.tf       # Output configuration
├── deploy.sh        # Deployment script
├── destroy.sh       # Cleanup script
├── azure.env        # Generated environment variables
└── README.md        # This file
```

## ⚙️ Configuration

You can customize the deployment by editing `variables.tf` or using a `terraform.tfvars` file:

```hcl
# terraform.tfvars
location            = "West Europe"
environment         = "prod"
openai_service_name = "my-ai-service"
```

## 🗑️ Cleanup

To remove all created resources:

```bash
chmod +x destroy.sh
./destroy.sh
```

## 💰 Cost Considerations

- **Azure OpenAI**: Pay-as-you-go based on usage
- **GPT-4**: ~$0.03 per 1K tokens (input) + $0.06 per 1K tokens (output)
- **Embeddings**: ~$0.0001 per 1K tokens
- **Resource Group**: No additional cost

Monitor usage in the Azure Portal to avoid unexpected charges.

## 🔍 Troubleshooting

### Azure OpenAI Access

If you get access denied errors, ensure your Azure subscription has Azure OpenAI access:

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to "Create a resource" → "Azure OpenAI"
3. Request access if needed

### Terraform Issues

```bash
# Re-initialize Terraform
terraform init -reconfigure

# Force refresh state
terraform refresh
```

### API Key Issues

Regenerate API keys if needed:

```bash
terraform taint azurerm_cognitive_account_key.main
terraform apply
```

## 📚 Learn More

- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/)
- [Terraform Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Azure OpenAI Pricing](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/)
