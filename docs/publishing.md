# Publishing This Kit As Its Own GitHub Repo

This guide assumes you want `generic-agent-retro-kit/` to become a standalone repository.

## Recommended GitHub repo name

Use:

- `agent-retro-kit`

Good alternatives:

- `coding-agent-retro-kit`
- `agent-delivery-retros`
- `agent-effectiveness-kit`

If you want the broadest, cleanest public name, `agent-retro-kit` is the best choice.

## What the initial public repo should contain

Commit these:

- `README.md`
- `LICENSE`
- `CONTRIBUTING.md`
- `.gitignore`
- `docs/`
- `templates/`
- `data/run-log-schema.md`
- `data/manual-log-template.md`
- `data/run-log.csv`
- `scorecards/.gitkeep`
- `retros/.gitkeep`
- `experiment-backlog.md`
- `decision-log.md`
- `scripts/bootstrap-weekly-cycle.sh`
- `scripts/log-run.sh`
- `examples/`

Do not commit generated week files in the first push.

## Suggested GitHub repo settings

- Visibility: private first, then public when you're happy with the wording
- Default branch: `main`
- Initialize with README: no
- Add license on GitHub: no, because the repo already contains one
- Add `.gitignore` on GitHub: no, because the repo already contains one

## Exact local commands

Run these from the parent directory that contains `generic-agent-retro-kit/`.

```bash
cp -R generic-agent-retro-kit agent-retro-kit
cd agent-retro-kit
rm -f scorecards/*.md retros/*.md
git init
git branch -M main
git add .
git commit -m "Initial commit"
git remote add origin git@github.com:YOUR_ORG_OR_USER/agent-retro-kit.git
git push -u origin main
```

If you prefer HTTPS:

```bash
git remote add origin https://github.com/YOUR_ORG_OR_USER/agent-retro-kit.git
git push -u origin main
```

## After clone or after first push

Create fresh working files locally:

```bash
./scripts/bootstrap-weekly-cycle.sh
```

That will seed the current ISO week into `scorecards/` and `retros/` without polluting the initial public commit.

## Notes

- `data/run-log.csv` is intentionally included as an empty starter file.
- Weekly generated files are ignored by default, so each workplace clone can create its own local retros.
- If you later want historical retros versioned in git, remove the relevant ignore rules intentionally rather than by accident.
