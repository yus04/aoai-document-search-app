// https://learn.microsoft.com/ja-jp/azure/cosmos-db/nosql/manage-with-bicep#azure-cosmos-db-account-with-analytical-store
// API Version: 2023-04-15

param accountName string
param databaseName string
resource account 'Microsoft.DocumentDB/databaseAccounts@2023-04-15' existing = {
  name: accountName
}

resource database 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2023-04-15' = {
  parent: account
  name: databaseName
  properties: {
    resource: {
      id: databaseName
    }
  }
}

output name string = database.name
