# Radiopharmaceutical USP 825 Agent

Experimental Python and browser-based **demonstration** for radiopharmaceutical-related metric screening. The repository includes two rule-based Python interfaces, a FastAPI service, an in-memory HMAC audit chain, and a static browser demonstration.

**Clinical and regulatory limitation:** This is **not** a USP <825> conformance evaluator, radiopharmaceutical quality-release system, or validated clinical decision support tool. Numeric limits in the code are arbitrary demonstration values, not USP requirements. Do not use the outputs for patient care, radiopharmaceutical release, radiation-safety decisions, or regulatory decisions. Never submit protected health information (PHI).

USP [General Chapter <825>](https://doi.usp.org/USPNF/USPNF_M11915_05_01.html) addresses preparation, compounding, dispensing, and repackaging of radiopharmaceuticals. Implementing its requirements requires a separately validated workflow.

## Implemented features

- Main rule evaluator: primary metric **>25**, secondary metric **>12**, critical boolean flag, and anomaly keywords. Three urgency categories.
- Separately maintained legacy nuclear evaluator: primary metric **>25**, secondary metric **>10**, critical flag, and protocol keywords. These are also arbitrary demo rules.
- FastAPI JSON endpoints: GET /health, GET /metrics, POST /api/audit, POST /api/chat, GET /api/audit/logs.
- Signed **in-memory** audit records using HMAC-SHA256 with chain verification. These are not durable across process restarts and do not constitute a regulated audit trail.
- Browser console at / when serving FastAPI. On static hosting, it runs a clearly labeled local demonstration with JSON export and no fabricated cryptographic signatures.
- CSV batch processing and synthetic-data stress simulation.

The /api/chat route provides a fixed mock response, **not** an LLM or validated medical reasoning. The /metrics endpoint returns JSON; the optional metrics exporter module is not connected to this endpoint.

## Installation and local use

Requires Python **3.10+**. Run the following from the repository root:

~~~bash
python -m pip install -e '.[test]'
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
python cli.py audit --task-id DEMO-1 --target SAMPLE-1 --primary 29 --secondary 14
python cli.py batch -i sample.csv -o results.csv
python cli.py verify-audit
python cli.py serve --host 127.0.0.1 --port 8000
~~~

Open http://127.0.0.1:8000/ for the console or http://127.0.0.1:8000/docs for FastAPI documentation. The installed command radiopharmaceutical-usp-825-agent executes the main CLI. The compatibility command radiopharmaceutical-usp-825-engine and python usp_825_nuclear_app.py execute the legacy nuclear path.

Input fields: task_id, target_identifier, primary_metric, secondary_metric, status_descriptor, is_critical_flag, and optional attributes. **Use synthetic IDs only.**

To preview the static browser demonstration, serve the web directory locally:

~~~bash
python -m http.server 8080 --directory web
~~~

Open http://127.0.0.1:8080/. The static demo performs client-side evaluation without contacting a backend.

## GitHub Pages

The Pages workflow publishes the static web directory on pushes to master. Static Pages hosting **does not run Python or FastAPI**, store audit logs, use an HMAC signing key, or send input to a backend. Publication and the live site must be verified before considering deployment complete.

## Docker

~~~bash
cp .env.example .env
# Replace AUDIT_SECRET_KEY with a securely generated random key.
docker compose up --build
~~~

Compose binds the API to 127.0.0.1:8000 on the host. The backend has **no authentication or authorization**. Do not expose it on a public network or use with sensitive records.

## Privacy and security

- The browser demonstration processes data locally and retains the latest result in memory until cleared/reloaded. JSON export is an explicit action. No third-party upload is performed by the demo.
- When a same-origin FastAPI backend is available, the entered data are transmitted to that service and selected identifiers/classifications may remain in memory.
- Regex filters attempt to block recognizable MRNs, SSNs, emails, telephone numbers, and some dates or names. **These are not comprehensive PHI detection, de-identification, or HIPAA compliance controls.**
- Configure AUDIT_SECRET_KEY on the server, not in the static HTML/JavaScript or repository. The HMAC key must be random and kept private.
- Audit-chain verification checks retained entry linkage and HMACs; it does not authenticate users, detect deletion of all records, or provide persistent audit storage.

## Tests

~~~bash
python -m pip install -e '.[test]'
pytest -q
python -m compileall -q agents usp_825_nuclear cli.py simulator.py enrichment.py
node --check web/app.js
node --test web/demo-engine.test.js
~~~

GitHub Actions runs Python 3.10–3.12 tests, JavaScript checks, and an audit-chain smoke test. The browser demonstration requires a modern browser with JavaScript, Fetch, Blob, and downloadable object URL support; full browser-compatibility certification is not claimed.

## Repository layout

- agents/: main evaluator, FastAPI app, HMAC chain, and deterministic mock responder.
- usp_825_nuclear/: separate legacy evaluator, CLI, and API.
- web/: standalone static demo and Node tests.
- enrichment.py: eight **unvalidated generic placeholder threshold modules**, not scientific calculators or USP compliance rules.
- tests/: Python unit and regression tests.
- Dockerfile, docker-compose.yml, .github/workflows/: container and deployment configuration.

## License

MIT. See [LICENSE](LICENSE).
