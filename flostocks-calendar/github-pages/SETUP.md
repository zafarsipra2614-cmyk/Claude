# Flostocks Content Calendar: setup

The calendar is one file, `index.html`, hosted free on GitHub Pages. Posts, captions and files are stored in a free Supabase project, and only people you create accounts for can sign in.

Setup takes about 10 minutes and is done once.

## 1. Create the Supabase project

1. Go to <https://supabase.com>, sign up (free) and click **New project**.
2. Name it `flostocks-calendar`, choose a database password (save it somewhere), and pick the region closest to you. Click **Create new project** and wait about a minute.

## 2. Create the database and file storage

1. In the left menu open **SQL Editor** and click **New query**.
2. Open `setup.sql` from this folder, copy everything, paste it in, and click **Run**. You should see "Success. No rows returned".

## 3. Turn off public sign-ups

Do this before publishing the site, so strangers can't create accounts.

1. Open **Authentication → Sign In / Providers** (on older dashboards: **Authentication → Providers**, or **Settings**).
2. Switch **Allow new users to sign up** off and save.
3. Leave the **Email** provider switched on.

## 4. Create the two accounts

1. Open **Authentication → Users** and click **Add user → Create new user**.
2. Enter your email and a password, tick **Auto Confirm User**, and click **Create user**.
3. Repeat for your social media manager, then send them their email and password.

Both accounts can add, edit, delete, download and change the status of posts.

## 5. Connect the page to Supabase

1. In Supabase, click **Connect** at the top of the project (or open **Project Settings → API**).
2. Copy the **Project URL** and the **anon public** key.
3. Open `index.html`, find these two lines near the bottom (search for `SUPABASE_URL`), and paste your values between the quotes:

   ```js
   const SUPABASE_URL = "PASTE_YOUR_PROJECT_URL_HERE";
   const SUPABASE_ANON_KEY = "PASTE_YOUR_ANON_KEY_HERE";
   ```

   The anon key is meant to be public. Without a signed-in account it can't read or change anything. Never paste the **service_role** key.

## 6. Publish on GitHub Pages

1. Upload `index.html` to your repository (in the root, or a `docs` folder).
2. In the repository open **Settings → Pages**, set **Source** to *Deploy from a branch*, choose your branch and folder, and click **Save**.
3. After a minute or two the site appears at `https://<your-username>.github.io/<repository-name>/`.

## Limits on the free plan

- Each file can be up to 50 MB. Compress larger videos before uploading.
- Total file storage is 1 GB. Delete old posts once they're published to free space.
- Supabase pauses free projects after a week with no activity. Opening the calendar regularly prevents this; if it does pause, click **Restore project** in the Supabase dashboard. No data is lost.

## Troubleshooting

| What you see | What to do |
| --- | --- |
| "Setup needed" message | The two values in step 5 are still the placeholders. |
| "That email and password don't match" | Check the account in **Authentication → Users**, or reset its password there. |
| "The calendar couldn't load: relation … does not exist" | Step 2 didn't run. Run `setup.sql` again. |
| Files won't upload | Check the `content` bucket exists under **Storage**, then run `setup.sql` again. |
