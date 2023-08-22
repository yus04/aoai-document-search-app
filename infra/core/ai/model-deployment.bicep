// https://learn.microsoft.com/ja-jp/azure/templates/microsoft.cognitiveservices/accounts/deployments?pivots=deployment-language-bicep
// API Version: 2023-05-01

// param accountName string
// param deploymentName string = 'gpt-35-turbo'
// param capacity int = 20
// param skuName string = 'Standard'
// param format string = 'OpenAI'
// param version string = '0613'

// resource account 'Microsoft.CognitiveServices/accounts@2023-05-01' existing = {
//   name: accountName
// }

// resource deployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
//   name: deploymentName
//   sku: {
//     capacity: capacity
//     name: skuName
//   }
//   parent: account
//   properties: {
//     model: {
//       format: format
//       name: deploymentName
//       version: version
//     }
//   }
// }

// output endpoint string = account.properties.endpoint
// output name string = account.name
