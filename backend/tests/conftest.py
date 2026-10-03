import os

# must run before app import: debug serves /openapi.json and drops the Secure cookie flag,
# which the http TestClient needs
os.environ.setdefault("DEBUG", "true")
