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
param tags object = {}
param serviceName string = 'aoai-document-search'

param gptDeploymentName string = 'gptdeployment'
param searchIndexName string = 'gptkbindex'
param storageContainerName string = 'Items'
param cosmosDbName string = 'cosmosdb'
param cosmosDbContainerName string = 'cosmosdbcontainer'

param principalId string = ''
param environmentName string
param tenantId string = tenant().tenantId
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))

param userPrincipal string = 'User'

resource resourceGroup 'Microsoft.Resources/resourceGroups@2022-09-01' = {
  name: resourceGroupName
  location: location
  tags: tags
}

module aiServices 'core/ai/aiservices.bicep' = {
  name: 'ai-services-account'
  scope: resourceGroup
  params: {
    name: 'ai-services-${resourceToken}'
    location: location
    tags: tags
  }
}

module openAi 'core/ai/openai.bicep' = {
  name: 'openai-account'
  scope: resourceGroup
  params: {
    name: 'openai-${resourceToken}'
    location: location
    tags: tags
  }
}

module cosmosAccount 'core/db/cosmos-account.bicep' = {
  name: 'cosmos-account'
  scope: resourceGroup
  params: {
    name: 'cosmos-account-${resourceToken}'
    location: location
    tags: tags
  }
}

module cosmosDatabase 'core/db/cosmos-database.bicep' = {
  name: 'cosmos-database'
  scope: resourceGroup
  params: {
    accountName: cosmosAccount.outputs.name
    databaseName: cosmosDbName
  }
}

module cosmosContainer 'core/db/cosmos-container.bicep' = {
  name: 'cosmos-container'
  scope: resourceGroup
  params: {
    databaseName: '${cosmosAccount.outputs.name}/${cosmosDatabase.outputs.name}'
    containerName: cosmosDbContainerName
  }
}

module containerApps 'core/host/container-apps.bicep' = {
  name: serviceName
  scope: resourceGroup
  params: {
    containerAppsEnvironmentName: 'container-apps-environment'
    containerAppsName: 'container-apps-${resourceToken}'
    env: [
      {
        name: 'AZURE_KEY_VAULT_ENDPOINT'
        value: keyVault.outputs.endpoint
      }
      {
        name: 'COSMOS_DB_CONNECTION_STRING'
        value: cosmosAccount.outputs.connectionString
      }
      {
        name: 'COSMOS_DB_NAME'
        value: cosmosDbName
      }
      {
        name: 'COSMOS_DB_CONTAINER_NAME'
        value: cosmosDbContainerName
      }
      {
        name: 'AZURE_STORAGE_BLOB_ENDPOINT'
        value: storageAccount.outputs.primaryEndpoints.blob
      }
      {
        name: 'AZURE_STORAGE_ACCOUNT_KEY'
        value: storageAccount.outputs.key
      }
      {
        name: 'AZURE_STORAGE_ACCOUNT'
        value: storageAccount.outputs.name
      }
      {
        name: 'AZURE_STORAGE_CONTAINER'
        value: storageContainerName
      }
      {
        name: 'AZURE_COGNITIVE_SEARCH_ENDPOINT'
        value: cognitiveSearch.outputs.endpoint
      }
      {
        name: 'AZURE_COGNITIVE_SEARCH_KEY'
        value: cognitiveSearch.outputs.key
      }
      {
        name: 'AZURE_COGNITIVE_SEARCH_INDEX'
        value: searchIndexName
      }
      {
        name: 'AZURE_OPENAI_ENDPOINT'
        value: openAi.outputs.endpoint
      }
      {
        name: 'AZURE_OPENAI_KEY'
        value: openAi.outputs.key
      }
    ]
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
    name: 'keyvault-yyyymmdd'
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
        name: 'AzureOpenAiServiceKey'
        value: openAi.outputs.key
      }
      {
        name: 'AzureOpenAiGptDeployment'
        value: gptDeploymentName
      }
      {
        name: 'AzureAiServicesName'
        value: aiServices.outputs.name
      }
      {
        name: 'AzureAiServicesKey'
        value: aiServices.outputs.key
      }
      {
        name: 'AzureCognitiveSearchEndpoint'
        value: cognitiveSearch.outputs.endpoint
      }
      {
        name: 'AzureCognitiveSearchKey'
        value: cognitiveSearch.outputs.key
      }
      {
        name: 'AzureSearchIndex'
        value: searchIndexName
      }
      {
        name: 'AzureCosmosDbEndpoint'
        value: cosmosAccount.outputs.endpoint
      }
      {
        name: 'AzureCosmosDbConnectionString'
        value: cosmosAccount.outputs.connectionString
      }
      {
        name: 'AzureCosmosDbName'
        value: cosmosDbName
      }
      {
        name: 'AzureStorageAccountKey'
        value: storageAccount.outputs.key
      }
      {
        name: 'AzureStorageAccountName'
        value: storageAccount.outputs.name
      }
      {
        name: 'AzureCosmosDbContainerName'
        value: cosmosDbContainerName
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

output AZURE_ENV_NAME string = environmentName
output AZURE_LOCATION_NAME string = location
output AZURE_TENANT_ID string = tenantId
output AZURE_RESOURCE_GROUP string = resourceGroup.name

output AZURE_OPENAI_SERVICE_NAME string = openAi.outputs.name
output AZURE_OPENAI_ENDPOINT string = openAi.outputs.endpoint
output AZURE_OPENAI_GPT_DEPLOYMENT string = gptDeploymentName

output AZURE_COSMOSDB_NAME string = cosmosAccount.outputs.name
output AZURE_COSMOSDB_ENDPOINT string = cosmosAccount.outputs.endpoint

output AZURE_CONTAINER_ENVIRONMENT_NAME string = containerApps.outputs.environmentName
output AZURE_CONTAINER_APPS_NAME string = containerApps.outputs.containerAppsName
output AZURE_CONTAINER_URI string = containerApps.outputs.uri
output AZURE_COUTAINER_IMAGE_NAME string = containerApps.outputs.containerImageName
output AZURE_CONTAINER_REGISTRY_NAME string = containerRegistry.outputs.registryName
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerRegistry.outputs.registryLoginServer

output AZURE_SEARCH_INDEX_NAME string = searchIndexName
output AZURE_COGNITIVE_SEARCH_NAME string = cognitiveSearch.outputs.name
output AZURE_COGNITIVE_SEARCH_ENDPOINT string = cognitiveSearch.outputs.endpoint

output AZURE_KEY_VAULT_NAME string = keyVault.outputs.name
output AZURE_KEY_VAULT_ENDPOINT string = keyVault.outputs.endpoint

output AZURE_STORAGE_ACCOUNT_NAME string = storageAccount.outputs.name
output AZURE_STORAGE_CONTAINER_NAME string = storageContainerName
output AZURE_STORAGE_BLOB_ENDPOINT string = storageAccount.outputs.primaryEndpoints.blob
