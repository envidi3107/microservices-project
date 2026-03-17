import yaml

with open(r'f:\bookstore-microservice\docker-compose.yml', 'r') as f:
    dc = yaml.safe_load(f)

manifests = []

for name, svc in dc['services'].items():
    is_pg = name.startswith('postgres')
    
    # Deployment
    image = svc.get('image', f'{name}:latest') if is_pg else f'{name}:latest'
    
    dep = {
        'apiVersion': 'apps/v1',
        'kind': 'Deployment',
        'metadata': {
            'name': name,
            'labels': {'app': name}
        },
        'spec': {
            'replicas': 1,
            'selector': {'matchLabels': {'app': name}},
            'template': {
                'metadata': {'labels': {'app': name}},
                'spec': {
                    'containers': [{
                        'name': name,
                        'image': image,
                        'imagePullPolicy': 'IfNotPresent'
                    }]
                }
            }
        }
    }
    
    if is_pg:
        dep['spec']['template']['spec']['containers'][0]['ports'] = [{'containerPort': 5432}]
        if 'environment' in svc:
            env_vars = []
            for k, v in svc['environment'].items():
                env_vars.append({'name': k, 'value': str(v)})
            dep['spec']['template']['spec']['containers'][0]['env'] = env_vars
    else:
        dep['spec']['template']['spec']['containers'][0]['ports'] = [{'containerPort': 8000}]
        if 'command' in svc:
            cmd = svc['command']
            if isinstance(cmd, str):
                dep['spec']['template']['spec']['containers'][0]['command'] = cmd.split()
            else:
                dep['spec']['template']['spec']['containers'][0]['command'] = cmd
            
    manifests.append(dep)
    
    # Service
    svc_type = "NodePort" if name == "api-gateway" else "ClusterIP"
    port = 5432 if is_pg else 8000
    
    ser = {
        'apiVersion': 'v1',
        'kind': 'Service',
        'metadata': {
            'name': name,
            'labels': {'app': name}
        },
        'spec': {
            'type': svc_type,
            'selector': {'app': name},
            'ports': [{
                'port': port,
                'targetPort': port
            }]
        }
    }
    manifests.append(ser)

with open(r'f:\bookstore-microservice\k8s-manifest.yaml', 'w') as f:
    for doc in manifests:
        f.write('---\n')
        yaml.safe_dump(doc, f, default_flow_style=False, sort_keys=False)

print("Generated k8s-manifest.yaml successfully.")
