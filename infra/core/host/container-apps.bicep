// https://learn.microsoft.com/ja-jp/azure/templates/microsoft.app/containerapps?pivots=deployment-language-bicep
// API Version: 2023-05-01

param containerAppsEnvironmentName string
param location string = resourceGroup().location
param tags object = {}
param serviceNameTags object = {}

param containerAppsName string
param env array = []
param identityName string = ''

param revisionMode string = 'Single'
param ingressEnabled bool = true
param external bool = true
param targetPort int = 80
param transport string = 'auto'
param allowedOrigins array = []
param corsPolicy object = {
  allowedOrigins: union([ 'https://portal.azure.com', 'https://ms.portal.azure.com' ], allowedOrigins)
}

param imageName string = ''
param containerCpuCoreCount string = '0.5'
param containerMemory string = '1.0Gi'
param containerMaxReplicas int = 1
param containerMinReplicas int = 1

resource userIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = if (!empty(identityName)) {
  name: identityName
}

module containerAppsEnvironment 'container-apps-environment.bicep' = {
  name: containerAppsEnvironmentName
  params: {
    name: containerAppsEnvironmentName
    location: location
    tags: tags
  }
}

resource containerApps 'Microsoft.App/containerApps@2023-05-01' = {
  name: containerAppsName
  location: location
  tags: serviceNameTags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: { '${userIdentity.id}': {} } 
  }
  properties: {
    managedEnvironmentId: containerAppsEnvironment.outputs.environmentId
    configuration: {
      activeRevisionsMode: revisionMode
      ingress: ingressEnabled ? {
        external: external
        targetPort: targetPort
        transport: transport
        corsPolicy: corsPolicy
      }: null
    }
    template: {
      containers: [
        {
          image: imageName
          name: containerAppsName
          env: env
          resources: {
            cpu: json(containerCpuCoreCount)
            memory: containerMemory
          }
        }
      ]
      scale: {
        maxReplicas: containerMaxReplicas
        minReplicas: containerMinReplicas
      }
    }
  }
}

output defaultDomain string = containerAppsEnvironment.outputs.defaultDomain
output environmentName string = containerAppsEnvironment.name
output environmentId string = containerAppsEnvironment.outputs.environmentId
output uri string = ingressEnabled ? 'https://${containerApps.properties.configuration.ingress.fqdn}' : ''
output containerImageName string = containerApps.properties.template.containers[0].image
output containerAppsName string = containerApps.name
