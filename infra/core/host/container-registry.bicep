// https://learn.microsoft.com/ja-jp/azure/templates/microsoft.containerregistry/registries?pivots=deployment-language-bicep
// API version: 2023-01-01-preview

param name string
param location string = resourceGroup().location
param tags object = {}
param sku object = {
  name: 'Standard'
}
// param identity object
param identity object = {
  type: 'SystemAssigned'
}

param adminUserEnabled bool = false
param anonymousPullEnabled bool = true
param dataEndpointEnabled bool = false
param encryption object = {
  status: 'disabled'
}
param networkRuleBypassOptions string = 'AzureServices'
param publicNetworkAccess string = 'Enabled'
param zoneRedundancy string = 'Disabled'

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name: name
  location: location
  tags: tags
  sku: sku
  identity: identity
  properties: {
    adminUserEnabled: adminUserEnabled
    anonymousPullEnabled: anonymousPullEnabled
    dataEndpointEnabled: dataEndpointEnabled
    encryption: encryption
    networkRuleBypassOptions: networkRuleBypassOptions
    publicNetworkAccess: publicNetworkAccess
    zoneRedundancy: zoneRedundancy
  }
}

output registryLoginServer string = containerRegistry.properties.loginServer
output registryName string = containerRegistry.name
