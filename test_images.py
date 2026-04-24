import os
import json

found = []
for dp, dn, filenames in os.walk('static/img/prendas/Policia'):
    for f in filenames:
        if 'buso' in f.lower() or 'verde' in f.lower():
            found.append(os.path.join(dp, f).replace('\\', '/'))

print(json.dumps(found, indent=2))
