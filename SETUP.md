# How to put this live

Everything here goes into a repo named exactly **`majedahdab2005`** (same as your username).
That is the special repo GitHub shows on your profile page.

## 1. Create the repo

On GitHub: **New repository** → name it `majedahdab2005` → **Public** → create it empty (no README).

## 2. Push the files

From the folder that contains `README.md` and `assets/`:

```bash
git init
git add .
git commit -m "profile: new green terminal profile"
git branch -M main
git remote add origin https://github.com/majedahdab2005/majedahdab2005.git
git push -u origin main
```

Or drag the files into the web uploader if you prefer. Keep the folder structure:

```
README.md
assets/            (all the .svg files)
.github/workflows/snake.yml
```

## 3. Turn on the contribution snake

The snake image in the METRICS section comes from a GitHub Action. Once:

1. Repo → **Settings** → **Actions** → **General** → Workflow permissions → **Read and write permissions** → Save.
2. Repo → **Actions** tab → enable workflows → pick **generate contribution snake** → **Run workflow**.

It creates an `output` branch with `snake.svg`, then refreshes itself every 12 hours.
Until you run it once, that one image shows as broken. Delete the snake `<p>` block from
`README.md` if you would rather not use it.

## 4. Make the stats count your Kagu work

Your commits mostly live under the `KaguSoftware` org, so the stats card will look thin
unless GitHub can attribute them to you:

- Org page → **People** → find yourself → set your membership to **Public**.
- Make sure the email you commit with is added to your GitHub account
  (Settings → Emails), otherwise those commits are not linked to you.

## 5. Finishing touches on the profile itself

- Set your GitHub bio to something short, e.g.
  `Co-founder @KaguSoftware · frontend, design and UX · Istanbul`
- Pin: TouchPadel, KaguOs, Real-Estate-Manager, UpperDeck, Kagu-website.
- Add `kagusoftware.com` in the profile website field.

## Editing later

| What | Where |
|---|---|
| Name, rotating job titles, university line | `assets/header.svg` |
| The role.json block | `assets/roles.svg` |
| Stack pipeline and tool chips | `assets/stack.svg` |
| Project cards | `assets/p-*.svg` |
| Emails, phones, location | `assets/footer.svg` |
| Section titles | `assets/s-*.svg` |

They are plain text SVG. Open one, change the text between `>` and `</text>`, save, push.

Colors used everywhere:

```
background   #05080A
deep green   #0E8F3C
main green   #1BE45C
bright green #4DFF8A
body text    #DCEFE2
muted text   #6E8C79
```
