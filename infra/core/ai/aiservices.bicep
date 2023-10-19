// https://learn.microsoft.com/ja-jp/azure/templates/microsoft.cognitiveservices/accounts?pivots=deployment-language-bicep
// API Version: 2023-05-01

param name string
param location string = resourceGroup().location
param tags object = {}
param sku object = {
  name: 'S0'
}
param kind string = 'CognitiveServices'
param staticWebsiteEnabled bool = false

resource aiServicesAccount 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: name
  location: location
  tags: tags
  sku: sku
  kind: kind
  properties: {
    apiProperties: {
      statisticsEnabled: staticWebsiteEnabled
    }
  }
}

output endpoint string = aiServicesAccount.properties.endpoint
output name string = aiServicesAccount.name
output key string = aiServicesAccount.listKeys().key1
