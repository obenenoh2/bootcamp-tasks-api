# Resource Group
resource "azurerm_resource_group" "rg" {
  name     = "rg-${var.project_name}-${var.environment}"
  location = var.location
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Azure Container Registry (ACR)
resource "azurerm_container_registry" "acr" {
  name                = "acr${var.project_name}${var.environment}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = true
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Azure Kubernetes Service (AKS)
resource "azurerm_kubernetes_cluster" "aks" {
  name                = "aks-${var.project_name}-${var.environment}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = "${var.project_name}-${var.environment}"
  
  default_node_pool {
    name       = "systempool"
    node_count = 3
    vm_size    = "Standard_B2s"
    os_disk_size_gb = 30
  }
  
  identity {
    type = "SystemAssigned"
  }
  
  network_profile {
    network_plugin = "azure"
    load_balancer_sku = "standard"
  }
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Azure Database for PostgreSQL Flexible Server
resource "azurerm_postgresql_flexible_server" "postgres" {
  name                   = "postgres-${var.project_name}-${var.environment}"
  resource_group_name    = azurerm_resource_group.rg.name
  location               = azurerm_resource_group.rg.location
  administrator_login    = var.db_username
  administrator_password = var.db_password
  sku_name              = "B_Standard_B1ms"
  version               = "15"
  storage_mb            = 32768
  geo_redundant_backup_enabled = false
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "azurerm_postgresql_flexible_server_database" "taskly" {
  name      = "taskly"
  server_id = azurerm_postgresql_flexible_server.postgres.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

# Azure Managed Redis
resource "azurerm_redis_cache" "redis" {
  name                = "redis-${var.project_name}-${var.environment}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  capacity            = 2
  family              = "C"
  sku_name            = "Standard"
  non_ssl_port_enabled = false
  minimum_tls_version = "1.2"

  redis_configuration {
    # Default configuration
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Azure Monitor Workspace (for Prometheus)
resource "azurerm_monitor_workspace" "monitor" {
  name                = "amw-${var.project_name}-${var.environment}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Outputs
output "kube_config" {
  value     = azurerm_kubernetes_cluster.aks.kube_config_raw
  sensitive = true
}

output "aks_cluster_name" {
  value = azurerm_kubernetes_cluster.aks.name
}

output "acr_login_server" {
  value = azurerm_container_registry.acr.login_server
}

output "postgres_connection_string" {
  value     = "postgresql://${var.db_username}:${var.db_password}@${azurerm_postgresql_flexible_server.postgres.fqdn}:5432/taskly"
  sensitive = true
}

output "redis_hostname" {
  value = azurerm_redis_cache.redis.hostname
}

output "redis_port" {
  value = 6379
}

output "redis_connection_string" {
  value = "redis://${azurerm_redis_cache.redis.hostname}:6379"
  sensitive = true
}

output "redis_primary_access_key" {
  value     = azurerm_redis_cache.redis.primary_access_key
  sensitive = true
}

output "acr_username" {
  value     = azurerm_container_registry.acr.admin_username
  sensitive = true
}

output "acr_password" {
  value     = azurerm_container_registry.acr.admin_password
  sensitive = true
}
