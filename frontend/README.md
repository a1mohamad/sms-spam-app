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

## Production container

```sh
docker build -t sms-spam-frontend .
docker run --rm -p 8080:8080 sms-spam-frontend
```

The Nginx image serves the SPA and proxies `/api/*` to `API_UPSTREAM`, whose
default is `sms-spam-api-gou5.onrender.com`.
