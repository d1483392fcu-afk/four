import importlib.util
from pathlib import Path

path = Path('four/app.py')
spec = importlib.util.spec_from_file_location('mainapp', path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
app = m.app
print('App loaded from', path)
print('Routes:', [rule.rule for rule in app.url_map.iter_rules()])
with app.test_client() as client:
    r = client.get('/')
    print('GET / status:', r.status_code)
    print('GET / body:', r.get_data(as_text=True).strip())
    r2 = client.get('/target')
    print('GET /target status:', r2.status_code)
    print('GET /target Location:', r2.headers.get('Location'))
