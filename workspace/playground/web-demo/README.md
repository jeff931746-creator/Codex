# Web Demo Deployment

This demo is deployed as a standalone static site through GitHub Pages.

This demo follows the root workspace session protocol in [`/Users/mt/Documents/Codex/CLAUDE.md`](/Users/mt/Documents/Codex/CLAUDE.md).

Expected site URL:

- `https://jeff931746-creator.github.io/Codex/`

Deployment source:

- GitHub Actions workflow: `.github/workflows/deploy-web-demo.yml`
- Published directory: `playground/web-demo`

If you want to bind a custom domain later:

1. Add a `CNAME` file into `playground/web-demo/`
2. Put the custom domain in that file, for example `demo.example.com`
3. Point the domain DNS to GitHub Pages

Because this site is pure static HTML/CSS/JS, no extra build step is required.
