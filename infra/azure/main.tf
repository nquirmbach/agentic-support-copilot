terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = "f2e05639-207c-41db-b193-c0bcb93ce888"
  tenant_id       = "dd01ae66-67c3-46f0-b2b6-f441fd73558b"
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location

  tags = {
    Project     = "Agentic Support Copilot"
    Environment = var.environment
    Purpose     = "AI Services"
  }
}

# Azure OpenAI Service
resource "azurerm_cognitive_account" "openai" {
  name                = var.openai_service_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  kind                = "OpenAI"
  sku_name            = var.sku_name

  tags = {
    Project     = "Agentic Support Copilot"
    Environment = var.environment
    Purpose     = "AI Services"
  }
}

# GPT-4o Deployment
resource "azurerm_cognitive_deployment" "gpt4o" {
  name                 = var.gpt4_deployment_name
  cognitive_account_id = azurerm_cognitive_account.openai.id

  model {
    format  = "OpenAI"
    name    = "gpt-4o"
    version = "2024-05-13"
  }

  sku {
    name = "Standard"
  }
}

# Text Embedding Deployment
resource "azurerm_cognitive_deployment" "embedding" {
  name                 = var.embedding_deployment_name
  cognitive_account_id = azurerm_cognitive_account.openai.id

  model {
    format  = "OpenAI"
    name    = "text-embedding-ada-002"
    version = "2"
  }

  sku {
    name = "Standard"
  }
}
