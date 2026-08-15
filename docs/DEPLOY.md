# Deploying

Three levels. Start at level 1 and stop whenever you have what you need.

| Level | What you get | Time | Cost |
|---|---|---|---|
| 1 | A public link to the dashboard | 2 minutes | free |
| 2 | The React app on Vercel, updating from GitHub | 20 minutes | free |
| 3 | The Python API and database live | 1 hour | free tiers |

---

# Read this before you deploy anything

**A public link is public.** Anyone with the URL sees every department's
adoption score. That is fine while the numbers are sample data. It is not fine
once they are real, because the survey promised staff that results stay inside
the company.

So:

- **Sample data** → any of the levels below, share freely
- **Real survey results** → put it behind a login, or host it on SharePoint
  where staff already sign in

Level 3 has the login built. Until then, keep real numbers off a public URL.

---

# Level 1 · A link in two minutes

No account, no install, no terminal.

1. Go to **https://app.netlify.com/drop**
2. Drag the `standalone` folder from your computer onto the page
3. Wait a few seconds

You get a URL like `https://calm-pastry-a1b2c3.netlify.app`. Send it to anyone.

To update the numbers later: edit `standalone/data.json` and drag the folder on
again. You get a new URL unless you create a free account and claim the site.

This is the right choice for showing the client this week.

---

# Level 2 · Vercel, properly

This is the version for your portfolio. It rebuilds automatically every time you
push a change.

## Step 1 · Create a GitHub account

Skip if you have one. Go to **https://github.com** and sign up.

## Step 2 · Install Git

Check whether you already have it. In VS Code, open a terminal and type:

```
git --version
```

If it prints a version, skip ahead. If not, download it from
**https://git-scm.com/downloads** and install with all the defaults, then close
and reopen VS Code.

## Step 3 · Turn the project into a repository

In VS Code, open a terminal. Make sure you are in the **rak-ai-adoption**
folder, not inside `frontend`. If the terminal line ends with `frontend`, type
`cd ..` first.

```
git init
git add .
git commit -m "AI Adoption Index"
```

The first time you commit, Git may ask who you are. If it does:

```
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
```

Then run the `git commit` line again.

## Step 4 · Push it to GitHub

1. Go to **https://github.com/new**
2. Repository name: `rak-ai-adoption`
3. Choose **Private**. It contains company context, so do not make it public
   until you have decided you want that.
4. Do **not** tick "Add a README". The repository must start empty.
5. Click **Create repository**

GitHub then shows you a page of commands. Use the ones under
"push an existing repository", which look like this:

```
git remote add origin https://github.com/YOUR-USERNAME/rak-ai-adoption.git
git branch -M main
git push -u origin main
```

Replace `YOUR-USERNAME` with yours. It will ask you to sign in.

Refresh the GitHub page. Your files are there.

## Step 5 · Connect Vercel

1. Go to **https://vercel.com** and sign up with your GitHub account
2. Click **Add New** then **Project**
3. Find `rak-ai-adoption` in the list and click **Import**

Now the one setting that matters:

4. **Root Directory** → click Edit → choose **frontend**

This is the step people miss. Your repository has both the backend and the
frontend in it, and Vercel needs to know which one to build. Get this wrong and
the build fails with a confusing error about a missing package.json.

5. Everything else is detected automatically: framework Vite, build command
   `npm run build`, output `dist`
6. Click **Deploy**

Two or three minutes later you have a live URL.

## Step 6 · Updating it

From now on, any change you make:

```
git add .
git commit -m "what you changed"
git push
```

Vercel rebuilds and publishes within a minute. Nothing else to do.

## Publishing new survey results

Edit `frontend/public/data.json`, then push. The `vercel.json` file in the
project tells Vercel never to cache that file, so new numbers appear on the
first refresh rather than whenever a cache happens to expire.

---

# Level 3 · The Python API and database

Only needed when you want survey uploads and logins rather than editing a file.

## The database · Neon

1. Go to **https://neon.tech** and sign up
2. Create a project. Region: choose the closest one, for example Frankfurt
3. Copy the connection string. It looks like
   `postgresql://user:password@ep-xxx.eu-central-1.aws.neon.tech/neondb`
4. Change the beginning from `postgresql://` to `postgresql+psycopg://`

That last step matters. SQLAlchemy needs to know which driver to use, and the
error you get without it is not obvious.

## The API · Render

1. Go to **https://render.com** and sign up with GitHub
2. **New** then **Web Service**, and choose your repository
3. Settings:

| Field | Value |
|---|---|
| Root Directory | `backend` |
| Environment | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

4. Add environment variables:

| Key | Value |
|---|---|
| `DATABASE_URL` | your Neon string, with `+psycopg` |
| `SECRET_KEY` | a long random string, see below |
| `CORS_ORIGINS` | `["https://your-app.vercel.app"]` |

To generate a secret key, run this locally and copy the output:

```
python -c "import secrets; print(secrets.token_hex(32))"
```

Never reuse the example key from `.env.example`. Anyone who has read the
repository could forge a login token with it.

5. Deploy. The first build takes a few minutes.

Check it worked by opening `https://your-api.onrender.com/docs`.

## Create your admin account

In the Render dashboard, open the **Shell** tab and run:

```
ADMIN_EMAIL=you@rakproperties.ae ADMIN_PASSWORD='a-strong-password' python -m scripts.seed
```

That creates the 13 departments and your login. It is safe to run more than
once.

## Point the frontend at the API

In Vercel, go to your project, then **Settings → Environment Variables**, and add:

| Key | Value |
|---|---|
| `VITE_API_URL` | `https://your-api.onrender.com` |

Then redeploy from the Vercel dashboard.

## One thing to know about the free tier

Render's free plan puts a service to sleep after 15 minutes of inactivity. The
first request after that takes 30 to 50 seconds while it wakes up.

For a demo, open the dashboard a minute before you present. For daily use, the
paid tier is about 7 dollars a month, or host it on Azure App Service inside the
company tenant, which is likely what IT would prefer anyway.

---

# Which should you actually do

**This week, for the client:** Level 1. Two minutes, and you have a link.

**For your portfolio:** Level 2. It is the one you put on a CV, and the GitHub
repository is half the value.

**When real survey data exists:** Level 3, or move it inside SharePoint. Real
department scores should not sit on a public URL.
