provider "azurerm" {
  features {}
  
  subscription_id = "e25edaf1-efeb-4a43-b275-886306abd8a5"
  client_id       = "e035e6db-a33c-4bb1-8eb8-0efd3a153d01"
  client_secret   = "nhd8Q~eLxiiGzzybi_RRWRc6zsTgEhZl7Lg3jbxh"
  tenant_id       = "3e143e4e-a729-438b-94a3-22f42f4af714"
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
  administrator_login_password = "h@z3m6969!"
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
