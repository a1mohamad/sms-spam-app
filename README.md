# SMS Spam Classifier API

This project exposes an SMS spam classifier as a FastAPI service. It loads an
ONNX model once at startup, classifies requests as `ham` or `spam`, encrypts the
original message with Fernet, and stores the encrypted message and prediction
metadata in PostgreSQL.

This is an API rather than a graphical web application:

- `GET /` returns API metadata.
- `GET /health` checks that the API can reach PostgreSQL.
- `GET /docs` opens the interactive Swagger API documentation.
- `POST /predict` classifies and persists one SMS message.

## Runtime flow

1. The container starts Uvicorn on `0.0.0.0:$PORT`.
2. FastAPI validates the ONNX model, vocabulary, and label mapping.
3. The model is loaded and warmed up.
4. `MESSAGE_ENCRYPTION_KEY` is validated.
5. A request to `/predict` is tokenized and passed to ONNX Runtime.
6. The plaintext SMS is encrypted before it is given to the repository.
7. The encrypted message, classification, probability, threshold, request ID,
   and message length are committed to PostgreSQL.

## Run locally with Docker Compose

Create a local environment file:

```powershell
Copy-Item .env.example .env
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Put the generated value in `.env` as `MESSAGE_ENCRYPTION_KEY`, choose a strong
`POSTGRES_PASSWORD`, and start the stack:

```powershell
docker compose up --build --wait
```

Open <http://localhost:8000/docs>. To stop the containers without deleting the
database volume:

```powershell
docker compose down
```

## Deploy on Northflank

The repository is ready for Northflank's Dockerfile build flow. Keep the
PostgreSQL addon, migration job, and API service in the same Northflank project
so they can communicate privately.

### 1. Push the repository

Northflank builds from Git. Ensure the deployment commit, including the
`artifacts/sms-spam-model.onnx` file, is pushed to the `main` branch of the
GitHub repository.

### 2. Create a Northflank project

From the dashboard:

1. Select the team.
2. Select **Create new** and then **Project**.
3. Name it `sms-spam` and choose the region nearest the expected users.

The project region cannot be changed later.

### 3. Create PostgreSQL

Inside the project:

1. Select **Create new**, then **Addon**, then **PostgreSQL**.
2. Name it `sms-spam-db`.
3. PostgreSQL 16 matches the local Compose environment.
4. Choose the smallest suitable resources initially.
5. Keep public access disabled. The API and migration job can use the private
   project network.
6. Wait until the addon reports that it is ready.

### 4. Create runtime secrets

Create a runtime secret group named `sms-spam-runtime`.

Link the PostgreSQL addon and select its `POSTGRES_URI` connection string. Add
the alias `DATABASE_URL`, because that is the variable expected by this
application. The app automatically converts a `postgresql://` or `postgres://`
URL to the Psycopg 3 SQLAlchemy URL format.

Generate a Fernet key locally:

```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Add the output as a secret:

```text
MESSAGE_ENCRYPTION_KEY=<generated Fernet key>
```

Optional runtime configuration can be added to the same group:

```text
THRESHOLD=0.5
MAX_MESSAGE_LENGTH=1000
MAX_REQUEST_BODY_BYTES=16384
DB_CONNECT_TIMEOUT_SECONDS=3
```

Do not upload the local `.env` file or commit either production secret.

### 5. Create the API service

Create a **combined service** using the GitHub repository:

- Branch: `main`
- Build type: `Dockerfile`
- Build context: repository root
- Dockerfile: `/Dockerfile`
- Runtime resources: start with at least 0.5 vCPU and 512 MiB memory; use 1 GiB
  if model startup is memory-constrained
- Instances: `1` initially
- Command override: none
- Secret group: `sms-spam-runtime`

Add a public HTTP port:

- Container port: `8000`
- Protocol: `HTTP`
- Public access: enabled

The Dockerfile exposes port 8000 and also respects a platform-provided `PORT`
environment variable.

Add health checks on port 8000:

- Startup/readiness: HTTP `GET /health`, with an initial delay of about 20
  seconds
- Liveness: HTTP `GET /`

`/health` deliberately checks PostgreSQL, while `/` can confirm that the API
process itself is alive.

### 6. Run the database migrations

Create a manual Northflank job from the same repository, branch, Dockerfile,
and runtime secret group. Override the image command to:

```text
alembic upgrade head
```

Run the job once and confirm that it exits successfully. Run this job again
after deploying a revision that adds a database migration. For a more advanced
release process, place the migration job before the service deployment in a
Northflank release flow.

### 7. Verify the deployment

Use the public service URL:

```text
https://<northflank-host>/health
https://<northflank-host>/docs
```

Test a prediction from PowerShell:

```powershell
$body = @{ text = "Congratulations! You won a free prize. Claim it now!" } |
    ConvertTo-Json

Invoke-RestMethod `
    -Method Post `
    -Uri "https://<northflank-host>/predict" `
    -ContentType "application/json" `
    -Body $body
```

The response has this shape:

```json
{
  "label": "spam",
  "spam_probability": 0.98
}
```

The exact probability depends on the model.

## Northflank troubleshooting

- **Container exits immediately:** check for a missing or invalid
  `MESSAGE_ENCRYPTION_KEY`, or missing `DATABASE_URL`.
- **`/health` returns 503:** verify that the PostgreSQL `POSTGRES_URI` was
  linked and aliased to `DATABASE_URL`, and that both resources are in the same
  project.
- **`/predict` returns a persistence error:** run the Alembic migration job and
  inspect its logs.
- **Build cannot find model files:** confirm the ONNX, vocabulary, and label
  mapping files exist on the deployed Git branch.
- **Service has no public URL:** add or detect container port 8000 and enable
  public HTTP access.
- **Startup health check fails too early:** increase the initial delay or
  failure threshold to give ONNX Runtime time to load and warm the model.

## Frontend prototype

The `frontend` directory contains the SMS Spam Classifier React and TypeScript
prototype. It includes responsive dataset, training, and live API workspaces.

```powershell
make frontend-install
make frontend-dev
```

The production frontend uses a multi-stage Docker image: Vite builds the React
application and Nginx serves it on port 8080. Nginx also proxies `/api/*` to the
deployed FastAPI service, avoiding browser cross-origin configuration.

```powershell
make frontend-build
make frontend-image
```

## Development checks

Run tests that do not need a live PostgreSQL database:

```powershell
python -m pytest -m "not database and not deployment"
```

Common development and operations commands are available through the
repository `Makefile`:

```powershell
make help
make check
make up
make logs
make down
```

`make down` preserves the local PostgreSQL volume. Run `make help` for focused
test, migration, and model-conversion shortcuts.

The full CI workflow provisions PostgreSQL, applies Alembic migrations, runs
the test suite, builds the Docker image, and exercises the Compose deployment.
