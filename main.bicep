targetScope = 'resourceGroup'
param location string = resourceGroup().location
@maxLength(20)
param appName string = 'runbook-search'
@description('Full immutable ACR image reference: registry.azurecr.io/runbook-search@sha256:...')
param image string
param registryServer string
param pullIdentityId string
resource logs 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${appName}-logs'
  location: location
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
    workspaceCapping: { dailyQuotaGb: 1 }
  }
}
resource environment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: '${appName}-env'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logs.properties.customerId
        sharedKey: logs.listKeys().primarySharedKey
      }
    }
  }
}
resource app 'Microsoft.App/containerApps@2024-03-01' = {
  name: appName
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: { '${pullIdentityId}': {} }
  }
  properties: {
    managedEnvironmentId: environment.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8000
        allowInsecure: false
        transport: 'http'
      }
      registries: [{ server: registryServer, identity: pullIdentityId }]
    }
    template: {
      containers: [
        {
          name: 'runbook-search'
          image: image
          resources: { cpu: json('0.25'), memory: '0.5Gi' }
          probes: [
            { type: 'Startup', httpGet: { path: '/health', port: 8000 }, periodSeconds: 5, failureThreshold: 30 }
            { type: 'Readiness', httpGet: { path: '/health', port: 8000 }, periodSeconds: 10, failureThreshold: 3 }
            { type: 'Liveness', httpGet: { path: '/health', port: 8000 }, periodSeconds: 30, failureThreshold: 3 }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 1
        rules: [{ name: 'http', http: { metadata: { concurrentRequests: '10' } } }]
      }
    }
  }
}
output url string = 'https://${app.properties.configuration.ingress.fqdn}'
output logsWorkspaceId string = logs.id
