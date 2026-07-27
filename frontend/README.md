# SMS Spam Classifier frontend

React and TypeScript prototype for exploring the SMS Spam dataset, training
snapshot, and live classifier.

## Local development

```sh
npm install
npm run dev
```

Vite proxies `/api` to the deployed API configured by
`VITE_DEV_API_TARGET`.

## Tests

Unit and component tests use Vitest, React Testing Library, and MSW. Browser
journeys run in desktop and mobile Chromium through Playwright; the browser
suite also checks WCAG A/AA rules with axe.

```sh
npm run test:unit
npm run test:unit:watch
npx playwright install chromium
npm run test:e2e
```

The API is mocked in both suites, so frontend tests do not write to Neon or
depend on the Render service being awake.

## Production container

```sh
docker build -t sms-spam-frontend .
docker run --rm -p 8080:8080 sms-spam-frontend
```

The Nginx image serves the SPA and proxies `/api/*` to `API_UPSTREAM`, whose
default is `sms-spam-api-gou5.onrender.com`.

## Render deployment

The root `render.yaml` defines this container as the Blueprint-managed
`sms-spam-frontend` web service. Render builds with this directory as the Docker
context, exposes port 8080, and checks `/frontend-health`. Production deploys
are triggered by GitHub Actions through the
`RENDER_FRONTEND_DEPLOY_HOOK_URL` repository secret after all tests pass.
