// https://learn.microsoft.com/ja-jp/azure/templates/microsoft.keyvault/vaults/secrets?pivots=deployment-language-bicep
// API version: 2022-07-01

param keyVaultName string
param secrets array = []

// param name string
param tags object = {}

// param enabled bool = true
// param exp int = 0
// param nbf int = 0

// param contentType string
// param value string

resource keyVault 'Microsoft.KeyVault/vaults@2022-07-01' existing = {
  name: keyVaultName
}

resource keyVaultSecret 'Microsoft.KeyVault/vaults/secrets@2022-07-01' = [for secret in secrets:{
  name: secret.name
  tags: tags
  parent: keyVault
  properties: {
    attributes: {
      enabled: contains(secret, 'enabled') ? secret.enabled : true
      exp: contains(secret, 'exp') ? secret.exp : 0
      nbf: contains(secret, 'nbf') ? secret.nbf : 0
    }
    contentType: contains(secret, 'contentType') ? secret.contentType : 'string'
    value: secret.value
  }
}]

