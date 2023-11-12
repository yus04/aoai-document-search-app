// https://learn.microsoft.com/ja-jp/azure/cosmos-db/nosql/manage-with-bicep#azure-cosmos-db-account-with-analytical-store
// API Version: 2023-04-15

param databaseName string
param containerName string
param partitionKeyPath string = '/usage'
resource database 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2023-04-15' existing = {
  name: databaseName
}

resource container 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: database
  name: containerName
  properties: {
    resource: {
      id: containerName
      partitionKey: {
        paths: [
          partitionKeyPath
        ]
        kind: 'Hash'
      }
    }
  }
}
