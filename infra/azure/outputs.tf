output "resource_group_name" {
  description = "Name of the created resource group"
  value       = azurerm_resource_group.main.name
}

output "openai_service_name" {
  description = "Name of the created Azure OpenAI service"
  value       = azurerm_cognitive_account.openai.name
}

output "openai_endpoint" {
  description = "Endpoint URL for the Azure OpenAI service"
  value       = azurerm_cognitive_account.openai.endpoint
  sensitive   = true
}

output "openai_api_key" {
  description = "API key for the Azure OpenAI service"
  value       = azurerm_cognitive_account.openai.primary_access_key
  sensitive   = true
}

output "gpt4_deployment_name" {
  description = "Name of the GPT-4o deployment"
  value       = azurerm_cognitive_deployment.gpt4o.name
}

output "embedding_deployment_name" {
  description = "Name of the text embedding deployment"
  value       = azurerm_cognitive_deployment.embedding.name
}

output "environment_variables" {
  description = "Environment variables for the application"
  value = {
    AZURE_OPENAI_ENDPOINT                  = azurerm_cognitive_account.openai.endpoint
    AZURE_OPENAI_API_KEY                   = azurerm_cognitive_account.openai.primary_access_key
    AZURE_OPENAI_API_VERSION               = "2023-12-01-preview"
    AZURE_OPENAI_DEPLOYMENT_NAME           = azurerm_cognitive_deployment.gpt4o.name
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME = azurerm_cognitive_deployment.embedding.name
  }
  sensitive = true
}
