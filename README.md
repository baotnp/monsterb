# monsterb

Personal developer notes (Odoo integrations, mail, debugging). Static HTML, no build step.

- Site: https://monsterb.pages.dev/
- `notes/smtp_sink.py`: a dependency-free local SMTP sink that saves every message as an `.eml` file.

Deploy (Cloudflare Pages): copy `index.html`, `style.css` and `notes/*.html` to a folder and run
`wrangler pages deploy <folder> --project-name monsterb --branch main`.
