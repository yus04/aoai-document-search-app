// https://learn.microsoft.com/ja-jp/azure/templates/microsoft.documentdb/databaseaccounts?pivots=deployment-language-bicep
// API Version: 2023-04-15

param name string
param location string
param tags object
param kind string = 'GlobalDocumentDB'
param identity object = {
  type: 'SystemAssigned'
}
param defaultConsistencyLevel string = 'Session'
param publicNetworkAccess string = 'Enabled'
param databaseAccountOfferType string = 'Standard'

resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2023-04-15' = {
  name: name
  location: location
  tags: tags
  kind: kind
  identity: identity
  properties: {
    consistencyPolicy: {
      defaultConsistencyLevel: defaultConsistencyLevel
    }
    databaseAccountOfferType: databaseAccountOfferType
    locations: [
      {
        locationName: location
      }
    ]
    publicNetworkAccess: publicNetworkAccess
  }
}

output id string = cosmosAccount.id
output name string = cosmosAccount.name
output endpoint string = cosmosAccount.properties.documentEndpoint
output connectionString string = cosmosAccount.listConnectionStrings().connectionStrings[0].connectionString
