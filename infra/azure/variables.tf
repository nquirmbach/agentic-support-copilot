variable "resource_group_name" {
  description = "Name of the Azure resource group"
  type        = string
  default     = "rg-agentic-support-copilot"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "East US"
}

variable "environment" {
  description = "Environment tag for resources"
  type        = string
  default     = "dev"
}

variable "openai_service_name" {
  description = "Name of the Azure OpenAI service"
  type        = string
  default     = "ai-agentic-support"
}

variable "sku_name" {
  description = "SKU for Azure OpenAI service"
  type        = string
  default     = "S0"
}

variable "gpt4_deployment_name" {
  description = "Name of the GPT-4o deployment"
  type        = string
  default     = "gpt-4o"
}

variable "embedding_deployment_name" {
  description = "Name of the text embedding deployment"
  type        = string
  default     = "text-embedding-ada-002"
}
