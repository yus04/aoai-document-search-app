// https://learn.microsoft.com/ja-jp/azure/templates/microsoft.app/managedenvironments?pivots=deployment-language-bicep
// API Version: 2023-05-01

param name string
param location string
param tags object = {}
param properties object = {}

resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: name
  location: location
  tags: tags
  properties: properties
}

output defaultDomain string = containerAppsEnvironment.properties.defaultDomain
output environmentName string = containerAppsEnvironment.name
output environmentId string = containerAppsEnvironment.id
