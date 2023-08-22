// https://learn.microsoft.com/ja-jp/azure/templates/microsoft.keyvault/vaults/accesspolicies?pivots=deployment-language-bicep
// API version: 2022-07-01

param keyVaultName string
param name string = 'add'

param principalId string
param permissions object = { secrets: ['get', 'list'] }
param tenantId string = subscription().id

resource keyVault 'Microsoft.KeyVault/vaults@2022-07-01' existing = {
  name: keyVaultName
}

resource keyVaultAccessPolicies 'Microsoft.KeyVault/vaults/accessPolicies@2022-07-01' = {
  name: name
  parent: keyVault
  properties: {
    accessPolicies: [
      {
        objectId: principalId
        permissions: permissions
        tenantId: tenantId
      }
    ]
  }
}
