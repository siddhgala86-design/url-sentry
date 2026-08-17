# URL Sentry — Phishing URL Detector

A Flask + Python decision-support app for a SYBSCIT (NEP) cybersecurity
mini-project. Paste a URL → 5 Python checks run → risk score → safe/unsafe
verdict with a buzzer alert.

## Project structure

```
url_sentry/
├── app.py                  # all Python detection logic (Flask backend)
├── requirements.txt
├── .gitignore
├── templates/
│   └── index.html
├── static/
│   ├── css/style.css
│   └── js/script.js
└── logs/
    └── scan_history.txt    # created automatically on first scan
```

---

## 1. Run it locally

```bash
# from inside the url_sentry/ folder
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open the link it prints — usually **http://127.0.0.1:5000**.

Try `https://www.google.com` (SAFE) and
`http://paypal-secure-verify.xyz/login.php` (DANGEROUS, buzzer + alarm)
to demo both outcomes.

---

## 2. Push it to GitHub

```bash
cd url_sentry
git init
git add .
git commit -m "URL Sentry - phishing URL detector"
```

Then on github.com:
1. Click **New repository** → name it `url-sentry` → **Create repository**
   (don't add a README/gitignore there, you already have them).
2. Copy the commands GitHub shows under "…or push an existing repository":
   ```bash
   git remote add origin https://github.com/<your-username>/url-sentry.git
   git branch -M main
   git push -u origin main
   ```

Your code (minus `venv/` and `scan_history.txt`, thanks to `.gitignore`)
is now on GitHub.

---

## 3. Deploy it live on PythonAnywhere (free tier)

1. **Sign up** at pythonanywhere.com (free "Beginner" account is enough).

2. **Get the code onto PythonAnywhere** — open a **Bash console** from
   the Dashboard and run:
   ```bash
   git clone https://github.com/<your-username>/url-sentry.git
   ```
   (No GitHub? Use the **Files** tab instead and upload each file manually
   into a new `url-sentry` folder.)

3. **Create a virtualenv** in that same Bash console:
   ```bash
   cd url-sentry
   mkvirtualenv --python=/usr/bin/python3.10 url-sentry-env
   pip install -r requirements.txt
   ```
   (`mkvirtualenv` activates it automatically. If you reopen a console
   later, run `workon url-sentry-env` to reactivate it.)

4. **Create the web app**: go to the **Web** tab → **Add a new web app**
   → pick your domain → choose **Manual configuration** (not "Flask" —
   manual gives you full control) → pick the Python version matching
   your virtualenv (3.10).

5. **Point it at your virtualenv**: on the same Web tab, under
   **Virtualenv**, enter:
   ```
   /home/<your-username>/.virtualenvs/url-sentry-env
   ```

6. **Edit the WSGI file**: click the WSGI configuration file link near
   the top of the Web tab, delete everything in it, and replace with:
   ```python
   import sys
   path = '/home/<your-username>/url-sentry'
   if path not in sys.path:
       sys.path.insert(0, path)

   from app import app as application
   ```

7. **Set the source code / working directory** on the Web tab to:
   ```
   /home/<your-username>/url-sentry
   ```

8. Click the big green **Reload** button at the top of the Web tab.

9. Visit `https://<your-username>.pythonanywhere.com` — your scanner is live.

**Updating later:** after pushing new commits to GitHub, just run
`git pull` inside `~/url-sentry` in a Bash console, then hit **Reload**
on the Web tab again.

**Note:** PythonAnywhere's free tier resets the filesystem occasionally
and sleeps the app when idle for the day — fine for a class demo/viva,
not for a permanent production deployment.
