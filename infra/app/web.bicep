// // https://learn.microsoft.com/ja-jp/azure/templates/microsoft.managedidentity/userassignedidentities?pivots=deployment-language-bicep
// // API Version: 2023-01-31

// param keyVaultName string
// param name string
// param location string = resourceGroup().location
// param tags object = {}

// // param resourceGroupName string = resourceGroup().name

// resource keyVault 'Microsoft.KeyVault/vaults@2022-07-01' existing = {
//   name: keyVaultName
//   scope: resourceGroup()
// }

// resource webIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
//   name: name
//   location: location
//   tags: tags
// }

// module webKeyVaultAccess '../core/security/keyvault-access.bicep' = {
//   name: 'web-keyvault-access'
//   scope: resourceGroup()
//   params: {
//     keyVaultName: keyVault.name
//     name: 'string'
//     principalId: webIdentity.properties.principalId
//   }
// }
