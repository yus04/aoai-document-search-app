// https://learn.microsoft.com/ja-jp/azure/templates/microsoft.storage/storageaccounts?pivots=deployment-language-bicep
// API version: 2022-09-01

param name string
param location string = resourceGroup().location
param tags object = {}
param sku object = {
  name: 'Standard_LRS'
}
param kind string = 'BlobStorage'
param identity object = {
  type : 'SystemAssigned'
}
@allowed([
  'Cool'
  'Hot'
  'Premium'
])
param accessTier string = 'Hot'
param allowBlobPublicAccess bool = true
param allowCrossTenantReplication bool = false
param allowSharedKeyAccess bool = true

param defaultToOAuthAuthentication bool = false
@allowed([
  'AzureDosZone'
  'Standard'
])
param dosEndpointType string = 'Standard'
param publicNetworkAccess string = 'Enabled'
@allowed([
  'TLS1_0'
  'TLS1_1'
  'TLS1_2'
])
param minimumTlsVersion string = 'TLS1_2'
param networkAcls object = {
  bypass: 'AzureServices'
  defaultAction: 'Allow'
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: name
  location: location
  tags: tags
  sku: sku
  kind: kind
  identity: identity
  properties: {
    accessTier: accessTier
    allowBlobPublicAccess: allowBlobPublicAccess
    allowCrossTenantReplication: allowCrossTenantReplication
    allowSharedKeyAccess: allowSharedKeyAccess
    defaultToOAuthAuthentication: defaultToOAuthAuthentication
    dnsEndpointType: dosEndpointType
    minimumTlsVersion: minimumTlsVersion
    networkAcls: networkAcls
    publicNetworkAccess: publicNetworkAccess
  }
}


output name string = storageAccount.name
output primaryEndpoints object = storageAccount.properties.primaryEndpoints
