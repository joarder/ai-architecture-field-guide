#!/usr/bin/env bash
# Bootstrap script for macOS — sets up The AI Architecture Field Guide
# locally, previews it, and (optionally) publishes it to GitHub Pages.
#
# Usage:
#   chmod +x bootstrap.sh
#   ./bootstrap.sh
#
# Safe to re-run — every step checks before acting.

set -euo pipefail

BOLD=$(tput bold 2>/dev/null || echo "")
RESET=$(tput sgr0 2>/dev/null || echo "")
say() { echo "${BOLD}==> $1${RESET}"; }

# --- 1. Check prerequisites -------------------------------------------------
say "Checking prerequisites"

if ! command -v git &>/dev/null; then
  echo "git not found. Install Xcode Command Line Tools first: xcode-select --install"
  exit 1
fi

if ! command -v python3 &>/dev/null; then
  echo "python3 not found. Install via: brew install python"
  exit 1
fi
echo "  git:     $(git --version)"
echo "  python3: $(python3 --version)"

GH_CLI_AVAILABLE=false
if command -v gh &>/dev/null; then
  GH_CLI_AVAILABLE=true
  echo "  gh CLI:  $(gh --version | head -1)  (repo creation can be automated)"
else
  echo "  gh CLI:  not found — you'll create the GitHub repo manually (instructions below)."
  echo "           Optional: brew install gh"
fi

# --- 2. Python environment ---------------------------------------------------
say "Setting up a virtual environment (.venv)"
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo "  Installed: $(mkdocs --version)"

# --- 3. Local preview ---------------------------------------------------------
say "Local preview"
echo "  Run 'mkdocs serve' now (in a separate terminal) to preview at http://127.0.0.1:8000"
echo "  Skipping auto-launch so this script can continue — press Ctrl+C in that terminal to stop it later."

# --- 4. Git init + first commit ----------------------------------------------
say "Git repository"
if [ ! -d ".git" ]; then
  git init -b main
  git add .
  git commit -m "Initial commit: The AI Architecture Field Guide"
  echo "  Repo initialized and first commit made."
else
  echo "  Git repo already exists — skipping init."
fi

# --- 5. GitHub repo + remote --------------------------------------------------
say "GitHub repository"
read -rp "GitHub username: " GH_USER
read -rp "Repo name [ai-architecture-field-guide]: " REPO_NAME
REPO_NAME=${REPO_NAME:-ai-architecture-field-guide}

if git remote get-url origin &>/dev/null; then
  echo "  Remote 'origin' already set: $(git remote get-url origin)"
else
  if $GH_CLI_AVAILABLE; then
    read -rp "Create the GitHub repo now via gh CLI? [y/N] " CREATE_REPO
    if [[ "$CREATE_REPO" =~ ^[Yy]$ ]]; then
      gh repo create "$REPO_NAME" --public --source=. --remote=origin
    else
      git remote add origin "https://github.com/${GH_USER}/${REPO_NAME}.git"
      echo "  Remote added. Create the repo manually at https://github.com/new first if you haven't."
    fi
  else
    git remote add origin "https://github.com/${GH_USER}/${REPO_NAME}.git"
    echo "  Remote added. Create the repo manually at https://github.com/new first if you haven't."
  fi
fi

# --- 6. Fix repo_url placeholder in mkdocs.yml -------------------------------
say "Updating mkdocs.yml with your repo URL"
sed -i '' "s|YOUR-GITHUB-USERNAME|${GH_USER}|g" mkdocs.yml 2>/dev/null || \
  sed -i "s|YOUR-GITHUB-USERNAME|${GH_USER}|g" mkdocs.yml
git add mkdocs.yml
git commit -m "Set repo URL" --allow-empty-message -m "" &>/dev/null || true

# --- 7. Push ------------------------------------------------------------------
say "Push to GitHub"
read -rp "Push to origin main now? [y/N] " DO_PUSH
if [[ "$DO_PUSH" =~ ^[Yy]$ ]]; then
  git push -u origin main
  echo "  Pushed. The 'Deploy MkDocs to GitHub Pages' Action will run automatically."
  echo "  Once it finishes, go to: Settings -> Pages -> set Source to the 'gh-pages' branch."
  echo "  Your site will be live at: https://${GH_USER}.github.io/${REPO_NAME}/"
else
  echo "  Skipped. Push manually with: git push -u origin main"
fi

say "Done"
echo "Next time you edit a chapter: git add . && git commit -m 'update' && git push"
echo "That single push re-triggers the GitHub Action and republishes the site."
