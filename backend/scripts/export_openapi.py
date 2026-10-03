"""writes the api contract and a browsable swagger page to documentation/api/"""

import json
from pathlib import Path

from app.main import app

OUT = Path(__file__).resolve().parents[2] / "documentation" / "api"

# spec is inlined, so the page opens straight from disk (file:// can't fetch a sibling json)
PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>HackYeah match-api</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({ spec: __SPEC__, dom_id: "#swagger-ui", supportedSubmitMethods: [] });
  </script>
</body>
</html>
"""


def main() -> None:
    spec = json.dumps(app.openapi(), indent=2, ensure_ascii=False)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "openapi.json").write_text(spec + "\n", encoding="utf-8")
    (OUT / "index.html").write_text(PAGE.replace("__SPEC__", spec), encoding="utf-8")


if __name__ == "__main__":
    main()
