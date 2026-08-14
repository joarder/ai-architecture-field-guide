# The AI Architecture Field Guide

A living reference for architecting, governing, and costing agentic AI systems — plus an interactive Workload Architecture Analyzer. Built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/), published free on GitHub Pages.

## Quickstart on macOS

```bash
cd ai-architecture-field-guide
./bootstrap.sh
```

This will, step by step (asking before anything destructive or public):

1. Check you have `git` and `python3` (prompts the `brew install` command if not)
2. Create a local Python virtual environment and install MkDocs Material
3. `git init` and make the first commit
4. Ask for your GitHub username and repo name, wire up the remote (uses `gh` CLI if you have it — `brew install gh` — otherwise gives manual instructions)
5. Replace the `YOUR-GITHUB-USERNAME` placeholder in `mkdocs.yml` with your actual username
6. Push to GitHub, which triggers the included GitHub Action to build and publish automatically

Your site will be live at `https://YOUR-USERNAME.github.io/ai-architecture-field-guide/` a minute or two after the Action finishes — check the **Actions** tab on GitHub to watch it run, and set **Settings → Pages → Source → `gh-pages` branch** the first time (only needed once).

## Preview locally before publishing

```bash
source .venv/bin/activate   # if not already active
mkdocs serve
# open http://127.0.0.1:8000
```

## Manual setup (if you'd rather not run the script)

```bash
pip install mkdocs-material --break-system-packages   # or inside a venv, no flag needed
git init && git add . && git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/ai-architecture-field-guide.git
git push -u origin main
```

Then in the repo's **Settings → Pages**, set the source to the `gh-pages` branch. The included `.github/workflows/deploy.yml` handles the actual build/publish on every push — you don't need to run `mkdocs gh-deploy` by hand unless you want an out-of-band update.

## Keep it "living" — add a chapter later

1. Add a new `docs/NN-topic.md` file
2. Add it to the `nav:` section in `mkdocs.yml`
3. `git add . && git commit -m "add chapter" && git push`

That's the whole revision-management workflow: commits are your changelog, `git log`/`git diff` are your audit trail, and the Action republishes automatically. Tag a commit (`git tag v1.0`) whenever you want a citable snapshot.

## Editing the Workload Analyzer

The tool lives at `docs/assets/tool.html` — a single self-contained file (no build step). Edit the `LAYERS` array or the `analyze()` function's logic directly to extend it as the guide grows.

## Structure

```
bootstrap.sh              — one-command macOS setup + publish
mkdocs.yml                — site config + navigation
.github/workflows/deploy.yml — auto-publish on every push
docs/
  index.md                — landing page
  01-mcp.md .. 11-*.md     — chapters
  assets/tool.html         — the interactive analyzer
```
