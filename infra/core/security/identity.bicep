param identityName string
param location string = resourceGroup().location

resource userIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: identityName
  location: location
}

output identityId string = userIdentity.properties.principalId
