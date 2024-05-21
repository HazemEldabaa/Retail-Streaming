provider "azurerm" {
  features {}
  
  subscription_id = ""
  client_id       = ""
  client_secret   = ""
  tenant_id       = ""
}

resource "azurerm_resource_group" "retail-sales" {
  name     = "retail-sales-resources"
  location = "germanywestcentral"
}

resource "azurerm_sql_server" "retail-sales" {
  name                         = "retail-salessqlserver"
  resource_group_name          = azurerm_resource_group.retail-sales.name
  location                     = azurerm_resource_group.retail-sales.location
  version                      = "12.0"
  administrator_login          = "hazem"
  administrator_login_password = ""
}

resource "azurerm_sql_database" "retail-sales" {
  name                = "retail-salesdb"
  resource_group_name = azurerm_resource_group.retail-sales.name
  location            = azurerm_resource_group.retail-sales.location
  server_name         = azurerm_sql_server.retail-sales.name
  edition             = "Standard"
  requested_service_objective_name = "S1"
}

resource "azurerm_sql_firewall_rule" "retail-sales" {
  name                = "retail-sales-firewall-rule"
  resource_group_name = azurerm_resource_group.retail-sales.name
  server_name         = azurerm_sql_server.retail-sales.name
  start_ip_address    = "78.29.192.45"
  end_ip_address      = "78.29.192.45"
}
