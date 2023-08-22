// https://learn.microsoft.com/ja-jp/azure/templates/microsoft.resources/2022-09-01/resourcegroups?pivots=deployment-language-bicep
// API version: 2022-09-01

// azdを使ったアーキテクチャ
// https://learn.microsoft.com/ja-jp/azure/developer/azure-developer-cli/make-azd-compatible?pivots=azd-create

// https://learn.microsoft.com/ja-jp/azure/azure-resource-manager/bicep/deploy-to-subscription?tabs=azure-cli
// https://learn.microsoft.com/ja-jp/azure/azure-resource-manager/bicep/modules

// main.parameters.json
// https://learn.microsoft.com/ja-jp/azure/azure-resource-manager/bicep/parameter-files?tabs=JSON

// Bicep でのリソースの依存関係
// https://learn.microsoft.com/ja-jp/azure/azure-resource-manager/bicep/resource-dependencies

targetScope = 'subscription'

param resourceGroupName string = 'aoai-document-search-rg'
param location string = 'japaneast'
// param location string = 'eastus'
param tags object = {}
param serviceName string = 'aoai-document-search'

param gptDeploymentName string = 'gptdeployment'
param searchIndexName string = 'gptkbindex'
param storageContainerName string = 'Items'

param principalId string = ''
param environmentName string
param tenantId string = tenant().tenantId
// 最後の文字列は不要
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location, 'abcdefghijklmnopqrstuvwx'))

param userPrincipal string = 'User'
// param servicePrincipal string = 'ServicePrincipal'

resource resourceGroup 'Microsoft.Resources/resourceGroups@2022-09-01' = {
  name: resourceGroupName
  location: location
  tags: tags
}

module openAi 'core/ai/openai.bicep' = {
  name: 'openai-account'
  scope: resourceGroup
  params: {
    name: 'cognitive-service-${resourceToken}'
    location: location
    tags: tags
  }
}

module cosmosDb 'core/db/cosmos-db.bicep' = {
  name: 'cosmos-db'
  scope: resourceGroup
  params: {
    name: 'cosmos-db-${resourceToken}'
    location: location
    tags: tags
  }
}

module containerApps 'core/host/container-apps.bicep' = {
  name: serviceName
  scope: resourceGroup
  params: {
    containerAppsEnvironmentName: 'container-apps-environment'
    containerAppsName: 'container-apps-${resourceToken}'
    // identityId: userIdentity.outputs.identityId
    identityName: 'user-identity'
    location: location
    tags: tags
    serviceNameTags: union(tags, { 'azd-service-name': serviceName })
    imageName: 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
  }
}

module containerRegistry 'core/host/container-registry.bicep' = {
  name: 'container-registry'
  scope: resourceGroup
  params: {
    name: 'containerregistry${resourceToken}'
    location: location
    tags: tags
    // identity: 
  }
}

module cognitiveSearch 'core/search/cognitive-search.bicep' = {
  name: 'cognitive-search'
  scope: resourceGroup
  params: {
    name: 'cognitive-search-${resourceToken}'
    location: location
    tags: tags
    authOptions: {
      aadOrApiKey: {
        aadAuthFailureMode: 'http401WithBearerChallenge'
      }
    }
  }
}

module keyVault 'core/security/keyvault.bicep' = {
  name: 'keyvault'
  scope: resourceGroup
  params: {
    name: 'keyvault-${resourceToken}'
    location: location
    tags: tags
    principalId: principalId
  }
}

module keyVaultSecrets 'core/security/keyvault-secrets.bicep' = {
  name: 'keyvault-secrets'
  scope: resourceGroup
  params: {
    keyVaultName: keyVault.outputs.name
    tags: tags
    secrets: [
      {
        name: 'AzureOpenAiServiceEndpoint'
        value: openAi.outputs.endpoint
      }
      {
        name: 'AzureOpenAiGptDeployment'
        value: gptDeploymentName
      }
      {
        name: 'AzureCognitiveSearchEndpoint'
        value: cognitiveSearch.outputs.endpoint
      }
      {
        name: 'AzureSearchIndex'
        value: searchIndexName
      }
      {
        name: 'AzureCosmosDbEndpoint'
        value: cosmosDb.outputs.endpoint
      }
      {
        name: 'AzureStorageAccountEndpoint'
        value: storageAccount.outputs.primaryEndpoints.blob
      }
      {
        name: 'AzureStorageContainer'
        value: storageContainerName
      }
    ]
  }
}

module storageAccount 'core/storage/storage-account.bicep' = {
  name: 'storage-account'
  scope: resourceGroup
  params: {
    name: 'saccount${resourceToken}'
    location: location
    tags: tags
    sku: {
      name: 'Standard_LRS'
    }
  }
}

module userIdentity 'core/security/identity.bicep' = {
  scope: resourceGroup
  name: 'user-identity'
  params: {
    identityName: 'user-identity'
    location: location
  }
}

module openAiRoleUser 'core/security/role.bicep' = {
  scope: resourceGroup
  name: 'openai-role-user'
  params: {
    principalId: principalId
    roleDefinitionId: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
    principalType: userPrincipal
  }
}

module storageRoleUser 'core/security/role.bicep' = {
  scope: resourceGroup
  name: 'storage-role-user'
  params: {
    principalId: principalId
    roleDefinitionId: '2a2b9908-6ea1-4ae2-8e65-a410df84e7d1'
    principalType: userPrincipal
  }
}

module storageContribRoleUser 'core/security/role.bicep' = {
  scope: resourceGroup
  name: 'storage-contribute-role-user'
  params: {
    principalId: principalId
    roleDefinitionId: 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
    principalType: userPrincipal
  }
}

// module acrRole 'core/security/acr-role.bicep' =  {
//   scope: resourceGroup
//   name: 'registry-access'
//   params: {
//     principalId: userIdentity.outputs.identityId
//     containerRegistryName: 'containerregistry${resourceToken}'
//     principalType: servicePrincipal
//   }
// }

// module searchRoleUser 'core/security/role.bicep' = {
//   scope: resourceGroup
//   name: 'search-role-user'
//   params: {
//     principalId: principalId
//     roleDefinitionId: '1407120a-92aa-4202-b7e9-c0e197c71c8f'
//     principalType: userPrincipal
//   }
// }

// module searchContribRoleUser 'core/security/role.bicep' = {
//   scope: resourceGroup
//   name: 'search-contribute-role-user'
//   params: {
//     principalId: principalId
//     roleDefinitionId: '8ebe5a00-799e-43f5-93ac-243d3dce84a7'
//     principalType: userPrincipal
//   }
// }

// module searchSvcContribRoleUser 'core/security/role.bicep' = {
//   scope: resourceGroup
//   name: 'search-svccontribute-role-user'
//   params: {
//     principalId: principalId
//     roleDefinitionId: '7ca78c08-252a-4471-8644-bb5ff32d4ba0'
//     principalType: userPrincipal
//   }
// }

// module openAiRoleBackend 'core/security/role.bicep' = {
//   scope: resourceGroup
//   name: 'openai-role-backend'
//   params: {
//     principalId: userIdentity.outputs.identityId
//     roleDefinitionId: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
//     principalType: servicePrincipal
//   }
// }

// module storageRoleBackend 'core/security/role.bicep' = {
//   scope: resourceGroup
//   name: 'storage-role-backend'
//   params: {
//     principalId: userIdentity.outputs.identityId
//     roleDefinitionId: '2a2b9908-6ea1-4ae2-8e65-a410df84e7d1'
//     principalType: servicePrincipal
//   }
// }

// module searchRoleBackend 'core/security/role.bicep' = {
//   scope: resourceGroup
//   name: 'search-role-backend'
//   params: {
//     principalId: userIdentity.outputs.identityId
//     roleDefinitionId: '1407120a-92aa-4202-b7e9-c0e197c71c8f'
//     principalType: servicePrincipal
//   }
// }

output AZURE_ENV_NAME string = environmentName
output AZURE_LOCATION_NAME string = location
output AZURE_TENANT_ID string = tenantId
output AZURE_RESOURCE_GROUP string = resourceGroup.name

output AZURE_OPENAI_SERVICE_NAME string = openAi.outputs.name
output AZURE_OPENAI_ENDPOINT string = openAi.outputs.endpoint
output AZURE_OPENAI_GPT_DEPLOYMENT string = gptDeploymentName
// output AZURE_OPENAI_RESOURCE_GROUP string = openAiResourceGroup.name

output AZURE_COSMOSDB_NAME string = cosmosDb.outputs.name
output AZURE_COSMOSDB_ENDPOINT string = cosmosDb.outputs.endpoint
// output AZURE_COSMOSDB_RESOURCE_GROUP string = cosmosDbResourceGroup.name

output AZURE_CONTAINER_ENVIRONMENT_NAME string = containerApps.outputs.environmentName
output AZURE_CONTAINER_APPS_NAME string = containerApps.outputs.containerAppsName
output AZURE_CONTAINER_URI string = containerApps.outputs.uri
output AZURE_COUTAINER_IMAGE_NAME string = containerApps.outputs.containerImageName
output AZURE_CONTAINER_REGISTRY_NAME string = containerRegistry.outputs.registryName
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerRegistry.outputs.registryLoginServer
// output AZURE_CONTAINER_REGISTRY_RESOURCE_GROUP string = containerRegistry.outputs.registryName

output AZURE_SEARCH_INDEX_NAME string = searchIndexName
output AZURE_SEARCH_SERVICE_NAME string = cognitiveSearch.outputs.name
output AZURE_SEARCH_SERVICE_ENDPOINT string = cognitiveSearch.outputs.endpoint
// output AZURE_SEARCH_SERVICE_RESOURCE_GROUP string = cognitiveSearchResourceGroup.name

output AZURE_KEY_VAULT_NAME string = keyVault.outputs.name
output AZURE_KEY_VAULT_ENDPOINT string = keyVault.outputs.endpoint
// output AZURE_KEY_VAULT_RESOURCE_GROUP string = keyVaultResourceGroup.name

output AZURE_STORAGE_ACCOUNT_NAME string = storageAccount.outputs.name
output AZURE_STORAGE_CONTAINER_NAME string = storageContainerName
output AZURE_STORAGE_BLOB_ENDPOINT string = storageAccount.outputs.primaryEndpoints.blob
// output AZURE_STORAGE_RESOURCE_GROUP string = storageResourceGroup.name
