# Flostocks Content Calendar

A calendar of what goes out on each platform and when, hosted free on GitHub Pages:
**https://zafarsipra2614-cmyk.github.io/Content-Calendar/**

- Each post has a date, an optional time, what's being posted, its platforms, and a status: **Pending**, **Scheduled** or **Uploaded**.
- Anyone with the link can view the calendar. This repository is public, so the plan is public too.
- To add, edit, delete or change the status of posts, unlock editing with a GitHub access key (below).
- Posts are saved in [`posts.json`](https://github.com/zafarsipra2614-cmyk/Content-Calendar/blob/calendar-data/posts.json) on the `calendar-data` branch. Every change is a commit there, so you get a full history for free.

## Turn on the site (once)

1. In this repository open **Settings → Pages**.
2. Under **Build and deployment**, set **Source** to *Deploy from a branch*, choose **main** and **/ (root)**, and click **Save**.
3. After a minute or two the calendar is live at the link above.

## Unlock editing on a device

Each person who edits needs their own key. Make it once per person:

1. Sign in to GitHub and open <https://github.com/settings/personal-access-tokens/new>.
   - Your manager needs to be added as a collaborator first: **Settings → Collaborators → Add people** in this repository. Then they create their own key from their own GitHub account.
2. **Token name**: `Flostocks calendar`. **Expiration**: pick a date (up to a year), or *No expiration*.
3. **Resource owner**: your account. **Repository access**: *Only select repositories* → choose **Content-Calendar**.
4. Under **Permissions → Repository permissions**, set **Contents** to **Read and write**. Leave everything else as it is.
5. Click **Generate token** and copy it (it starts with `github_pat_`).
6. Open the calendar, click **Unlock editing**, paste the key, and click **Unlock**.

The key is saved only in that browser. Click **Lock editing** to remove it, for example on a shared computer. Treat it like a password: anyone who has it can change this repository.

> Collaborator keys: GitHub only lets you pick repositories you own when making a fine-grained key. If your manager's key screen doesn't list **Content-Calendar**, they can create a **classic** key instead at <https://github.com/settings/tokens/new> with the **public_repo** scope.

## Troubleshooting

| What you see | What to do |
| --- | --- |
| "That key can only read" | Edit the key on GitHub and set **Contents** to **Read and write**. |
| "That key can't see the Content-Calendar repository" | Edit the key and add **Content-Calendar** under **Repository access**. |
| "Your GitHub key isn't valid any more" | The key expired or was deleted. Click **Lock editing**, make a new key, and unlock again. |
| "GitHub is limiting requests from this network" | GitHub allows 60 views an hour per network without a key. Wait a few minutes, or unlock editing (keys get a much higher limit). |
