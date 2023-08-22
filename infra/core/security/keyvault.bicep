// https://learn.microsoft.com/ja-jp/azure/templates/microsoft.keyvault/vaults?pivots=deployment-language-bicep
// API version: 2022-07-01

param name string
param location string
param tags object = {}

param principalId string = ''
param permissions object = {
  secrets: [
    'get', 'list'
  ]
}
param tenantId string = subscription().tenantId
param sku object = {
  name: 'standard'
  family: 'A'
}

resource keyVault 'Microsoft.KeyVault/vaults@2022-07-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    accessPolicies: !empty(principalId) ? [
      {
        objectId: principalId
        permissions: permissions
        tenantId: tenantId
      }
    ] : []
    sku: sku
    tenantId: tenantId
  }
}

output endpoint string = keyVault.properties.vaultUri
output name string = keyVault.name
