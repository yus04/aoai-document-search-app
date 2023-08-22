// https://learn.microsoft.com/ja-jp/azure/templates/Microsoft.Search/searchServices?pivots=deployment-language-bicep
// API version: 2022-09-01

param name string
param location string = resourceGroup().location
param tags object = {}
param sku object = {
  name: 'basic'
}
param identity object = {
  type: 'SystemAssigned'
}
param authOptions object = {}
param disableLocalAuth bool = false
@allowed([
  'Disabled'
  'Enabled'
  'Unspecified'
])
param enforcement string = 'Unspecified'
param encryptionWithCmk object = {
  enforcement: enforcement
}
@allowed([
  'default'
  'highDensity'
])
param hostingMode string = 'default'
param networkRuleSet object = {
  ipRules: []
}
param partitionCount int = 1
@allowed([
  'disabled'
  'enabled'
])
param publicNetworkAccess string = 'enabled'
param replicaCount int = 1

resource search 'Microsoft.Search/searchServices@2022-09-01' = {
  name: name
  location: location
  tags: tags
  sku: sku
  identity: identity
  properties: {
    authOptions: authOptions
    disableLocalAuth: disableLocalAuth
    encryptionWithCmk: encryptionWithCmk
    hostingMode: hostingMode
    networkRuleSet: networkRuleSet
    partitionCount: partitionCount
    publicNetworkAccess: publicNetworkAccess
    replicaCount: replicaCount
  }
}

output endpoint string = 'https://${name}.search.windows.net/'
output name string = search.name
