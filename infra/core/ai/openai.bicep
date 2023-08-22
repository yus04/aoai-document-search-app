// https://learn.microsoft.com/ja-jp/azure/templates/microsoft.cognitiveservices/accounts?pivots=deployment-language-bicep
// API Version: 2023-05-01

param name string
param location string = resourceGroup().location
param tags object = {}
param sku object = {
  name: 'S0'
  tier: 'Standard'
  capacity: 1
}
param kind string = 'OpenAI'
param identity object = {
  type: 'SystemAssigned'
}
param publicNetworkAccess string = 'Enabled'

param deploymentName string = 'gpt-35-turbo'
param capacity int = 20
param skuName string = 'Standard'
param format string = 'OpenAI'
param version string = '0613'

resource openAiAccount 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: name
  location: location
  tags: tags
  sku: sku
  kind: kind
  identity: identity
  properties: {
    publicNetworkAccess: publicNetworkAccess
  }
}

resource deployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  name: deploymentName
  sku: {
    capacity: capacity
    name: skuName
  }
  parent: openAiAccount
  properties: {
    model: {
      format: format
      name: deploymentName
      version: version
    }
  }
}

output endpoint string = openAiAccount.properties.endpoint
output name string = openAiAccount.name
