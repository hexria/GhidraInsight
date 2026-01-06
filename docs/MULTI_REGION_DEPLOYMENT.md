# Multi-Region Deployment Guide

Deploy GhidraInsight across multiple regions for high availability and low latency.

## Overview

Multi-region support provides:
- **High Availability**: Automatic failover between regions
- **Low Latency**: Route requests to nearest region
- **Data Replication**: Synchronize data across regions
- **Disaster Recovery**: Continue operation if one region fails

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Global Load Balancer                  │
└───────────────┬─────────────────────────────────────────┘
                │
        ┌───────┴───────┬──────────────┐
        │               │              │
┌───────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
│  us-east-1   │ │  eu-west-1 │ │  ap-south-1 │
│  (Primary)   │ │            │ │            │
└───────┬──────┘ └─────┬──────┘ └─────┬──────┘
        │               │              │
        └───────────────┴──────────────┘
                    │
            ┌───────▼────────┐
            │  Replication  │
            │   (Async)     │
            └───────────────┘
```

## Configuration

### Enable Multi-Region

```yaml
# config.yaml
region:
  enabled: true
  current_region: "us-east-1"
  regions:
    - "us-east-1"
    - "eu-west-1"
    - "ap-south-1"
  replication_enabled: true
  replication_regions:
    - "eu-west-1"
    - "ap-south-1"
  primary_region: "us-east-1"
  failover_enabled: true
  cross_region_timeout: 30
```

### Environment Variables

```bash
export GHIDRA_REGION_ENABLED=true
export GHIDRA_REGION_CURRENT=us-east-1
export GHIDRA_REGION_PRIMARY=us-east-1
export GHIDRA_REGION_REPLICATION_ENABLED=true
```

## Deployment

### 1. Deploy to Each Region

```bash
# Deploy to us-east-1
kubectl apply -f k8s/ -n ghidrainsight-us-east-1

# Deploy to eu-west-1
kubectl apply -f k8s/ -n ghidrainsight-eu-west-1

# Deploy to ap-south-1
kubectl apply -f k8s/ -n ghidrainsight-ap-south-1
```

### 2. Configure Global Load Balancer

#### AWS (Route 53 + ALB)

```yaml
# Route 53 health checks
apiVersion: v1
kind: Service
metadata:
  name: ghidrainsight-global
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
spec:
  type: LoadBalancer
  ports:
  - port: 3000
```

#### GCP (Global Load Balancing)

```bash
# Create global forwarding rule
gcloud compute forwarding-rules create ghidrainsight-global \
  --global \
  --target-https-proxy ghidrainsight-https-proxy \
  --ports 443
```

#### Azure (Traffic Manager)

```bash
# Create Traffic Manager profile
az network traffic-manager profile create \
  --name ghidrainsight-global \
  --resource-group ghidrainsight-rg \
  --routing-method Performance
```

## Database Replication

### PostgreSQL Streaming Replication

```bash
# Primary (us-east-1)
postgresql.conf:
  wal_level = replica
  max_wal_senders = 3
  max_replication_slots = 3

# Standby (eu-west-1)
recovery.conf:
  primary_conninfo = 'host=us-east-1-db port=5432 user=replicator'
  primary_slot_name = 'eu_west_1_slot'
```

### Cross-Region Database Sync

```python
from ghidrainsight.core.multi_region import MultiRegionManager

manager = MultiRegionManager(settings)
await manager.initialize()

# Replicate analysis results
results = {"analysis_id": "123", "data": {...}}
await manager.replicate_to_all(results)
```

## Health Checks

### Automatic Health Monitoring

```python
# Check all regions
health_status = await manager.check_all_regions()

# Get best region
best_region = manager.get_best_region()

# Get region status
status = manager.get_region_status()
```

### Health Check Endpoint

```bash
# Check region health
curl https://ghidrainsight-us-east-1.example.com/health

# Response
{
  "status": "healthy",
  "region": "us-east-1",
  "latency_ms": 12.5
}
```

## Failover

### Automatic Failover

When primary region fails:
1. Health check detects failure
2. Load balancer routes to next healthy region
3. Database promotes standby to primary
4. Services continue operation

### Manual Failover

```bash
# Promote standby region to primary
kubectl patch configmap ghidrainsight-config \
  -n ghidrainsight-eu-west-1 \
  --patch '{"data":{"GHIDRA_REGION_PRIMARY":"eu-west-1"}}'
```

## Data Consistency

### Eventual Consistency

- Analysis results replicated asynchronously
- Cache invalidation across regions
- Database replication lag: < 1 second

### Strong Consistency (Optional)

For critical operations, use primary region:

```python
if manager.is_current_region_primary():
    # Perform write operation
    result = await write_to_database(data)
    # Replicate to other regions
    await manager.replicate_to_all(result)
else:
    # Route to primary
    await route_to_primary(data)
```

## Monitoring

### Region Status Dashboard

```python
# Get all region statuses
statuses = manager.get_region_status()

for region, status in statuses.items():
    print(f"{region}: {'✓' if status['healthy'] else '✗'} "
          f"({status['latency_ms']}ms)")
```

### Metrics

- Region health status
- Cross-region latency
- Replication lag
- Failover events

## Best Practices

1. **Primary Region**: Choose region closest to most users
2. **Replication**: Enable for critical data
3. **Health Checks**: Check every 30 seconds
4. **Failover**: Test regularly
5. **Monitoring**: Alert on region failures
6. **Data Locality**: Store data in user's region when possible

## Cost Optimization

- Use regional databases (cheaper than global)
- Replicate only critical data
- Cache aggressively to reduce cross-region calls
- Use CDN for static assets

## Troubleshooting

### Region Unreachable

```bash
# Check network connectivity
kubectl exec -it pod-name -- ping ghidrainsight-eu-west-1.example.com

# Check DNS resolution
kubectl exec -it pod-name -- nslookup ghidrainsight-eu-west-1.example.com
```

### Replication Lag

```sql
-- Check replication lag (PostgreSQL)
SELECT * FROM pg_stat_replication;
```

### Failover Issues

```bash
# Check health status
curl https://ghidrainsight-us-east-1.example.com/health

# Check region configuration
kubectl get configmap ghidrainsight-config -o yaml
```

---

For cloud-specific setup, see:
- [AWS Deployment](CLOUD_DEPLOYMENT_AWS.md)
- [GCP Deployment](CLOUD_DEPLOYMENT_GCP.md)
- [Azure Deployment](CLOUD_DEPLOYMENT_AZURE.md)
