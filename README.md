# TASQ Backend

FastAPI backend for the task management application.

## Vercel Deployment

This project uses FastAPI and SQLAlchemy. It does not use Prisma ORM, so on Vercel you should deploy it as a Python FastAPI app and connect it to your Vercel Postgres or Prisma Postgres database through environment variables.

### 1. Required environment variables

Set these in your Vercel project:

- `ALGORITHM`
- `SECRET_KEY`
- `EXP_TIME`
- `CORS_ORIGINS`

For the database, use one of these approaches:

- Preferred: set `DATABASE_URL` to your Postgres connection string
- Or connect Vercel Postgres and let Vercel inject `POSTGRES_URL`

The app automatically falls back in this order:

1. `DATABASE_URL`
2. `POSTGRES_URL`
3. `POSTGRES_PRISMA_URL`
4. `POSTGRES_URL_NON_POOLING`

### 2. Entry point

Vercel serves the app through `api/index.py`, which re-exports the FastAPI app from `main.py`.

### 3. Database tables

`AUTO_CREATE_TABLES` is disabled by default for deployment safety.

If you want SQLAlchemy to create tables automatically on startup, set:

```env
AUTO_CREATE_TABLES=true
```

That can help for a quick first deploy, but a migration tool such as Alembic is the better long-term setup.

### 4. NullPool on serverless

On Vercel, this app uses SQLAlchemy `NullPool` by default to avoid keeping database connections open across serverless executions. You can override that with `DB_USE_NULL_POOL=false` if needed.

### 5. Deploy command

After pushing this repo to GitHub and importing it into Vercel:

1. Add the environment variables above.
2. Redeploy the project.
3. Test `https://<your-project>.vercel.app/health`

### 6. Common failure cases

- Missing `DATABASE_URL` or Vercel Postgres connection
- `CORS_ORIGINS` does not include your frontend Vercel URL
- `AUTO_CREATE_TABLES=false` with an empty database and no migrations yet
- Using Prisma-specific expectations in a project that is actually SQLAlchemy-based
