# How to deploy to Kubernetes
### Generate secret from config

Config json file is preset on filesystem under /tmp/config.json
```json
{
    "ups1_name": {
        "address": "https://address.to.ups1",
        "user": "username",
        "password": "password"
    },
    "ups2_name": {
        "address": "https://address.to.ups2",
        "user": "username",
        "password": "password"
    }
}
```

```bash
cat /tmp/config.json | base64 -w 0
```

Simply copy the base64 encoded string into the kubernetes secret manifest next to config.json
```yaml
---
apiVersion: v1
kind: Secret
metadata:
  name: prometheus-eaton-ups-exporter-config
data:
  config.json: ewogICAgInVwczFfbmFtZSI6IHsKICAgICAgICAiYWRkcmVzcyI6ICJodHRwczovL2FkZHJlc3MudG8udXBzMSIsCiAgICAgICAgInVzZXIiOiAidXNlcm5hbWUiLAogICAgICAgICJwYXNzd29yZCI6ICJwYXNzd29yZCIKICAgIH0sCiAgICAidXBzMl9uYW1lIjogewogICAgICAgICJhZGRyZXNzIjogImh0dHBzOi8vYWRkcmVzcy50by51cHMyIiwKICAgICAgICAidXNlciI6ICJ1c2VybmFtZSIsCiAgICAgICAgInBhc3N3b3JkIjogInBhc3N3b3JkIgogICAgfQp9Cg==
```

### Deploy manifest to kubernetes
kubectl -n <your namespace> apply -f kubernetes/manifest.yaml
