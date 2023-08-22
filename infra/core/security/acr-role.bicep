// https://learn.microsoft.com/ja-jp/azure/templates/microsoft.authorization/roleassignments?pivots=deployment-language-bicep
// API version: 2022-04-01

// param userIdentityName string
param principalId string
param containerRegistryName string
param principalType string

var acrPullRole = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')

// resource userIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
//   name: userIdentityName
// }

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' existing = {
  name: containerRegistryName
}

resource acrRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: containerRegistry
  name: guid(subscription().id, resourceGroup().id, principalId, acrPullRole)
  properties: {
    roleDefinitionId: acrPullRole
    principalType: principalType
    principalId: principalId
  }
}
