# 🌌 Portfolio Webpage


![project_5](https://github.com/user-attachments/assets/48c96e72-bfe2-4325-8606-58f6efa55639)


Welcome to my **[Portfolio Webpage](https://falcontreras.com)** — a space where creativity and functionality meet! This project serves as a showcase of my skills, projects, and professional journey as a **Python developer**. Built with **Flask**, **HTML**, **CSS**, and **JavaScript**, this responsive and interactive website encapsulates who I am and what I bring to the table.

The website is **dockerized** for seamless deployment and scalability, hosted on **Google Cloud Platform (GCP)**, with static assets managed in **AWS S3**. It features a sleek, futuristic design with glowing elements and animations that make the browsing experience engaging and memorable.

You can check it out at [https://falcontreras.com](https://falcontreras.com).

---

### ✨ Features

- **Dynamic Projects Showcase**: An interactive slider to explore my portfolio projects in detail.
- **Skills Section**: Visual representation of my technical and interpersonal skills, grouped for clarity.
- **About Me**: A personal introduction highlighting my professional journey and philosophy.
- **Contact Form**: A functional contact form for direct communication, integrated with email handling.
- **Custom Styling**: Designed with a glowing, futuristic aesthetic for a unique user experience.
- **Responsive Design**: Optimized for all screen sizes, from desktops to smartphones.

---

### 🛠️ Tech Stack

#### 🌐 Frontend
- ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
- ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
- ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

#### 🧑‍💻 Backend
- ![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)

#### 🚀 Deployment
- ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
- ![Google Cloud](https://img.shields.io/badge/Google%20Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)

#### 📂 Asset Management
- ![AWS S3](https://img.shields.io/badge/AWS%20S3-232F3E?style=for-the-badge&logo=amazon-s3&logoColor=white)

---

### 🧑‍💻 Local Development

Dependencies are managed with [uv](https://docs.astral.sh/uv/). Python version is pinned in `.python-version`.

```bash
uv sync
uv run python main.py   # dev server on http://localhost:8080
```

The app won't start without a `.env` file (or equivalent environment variables in production) defining:

| Variable | Purpose |
|---|---|
| `KEY_ID`, `ACCESS_KEY`, `REGION`, `BUCKET` | AWS S3 access - source of truth for skills/projects/icons |
| `FLASK_KEY` | Session + CSRF signing secret |
| `MAIL_SERVER`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER` | Contact form email delivery (AWS SES) |
| `REFRESH_TOKEN` | Auth token for `POST /admin/refresh` (see below) |

In production these come from GCP Secret Manager / Cloud Run env vars, not a checked-in `.env`.

**Container**: `Dockerfile` runs the app under gunicorn (2 workers). Build/run with Docker or [Podman](https://podman.io/) interchangeably - `podman build`/`podman run` accept the same flags.

#### Refreshing content without a redeploy

`skills.json`/`projects.json`/icons are fetched from S3 once at process startup. To pick up changes without restarting the container:

```bash
curl -X POST -H "X-Refresh-Token: <REFRESH_TOKEN>" https://<host>/admin/refresh
```

Under gunicorn this triggers a graceful reload of every worker (not just the one that handles the request) - verified end-to-end via Podman, see commit history for details.

#### Project GIF images

Project preview GIFs live in S3 and are fetched at startup like everything else, **except** where a pre-optimized version has been committed to `static/optimized_projects/` (WebP, smaller than the source GIF - not all of them compress better, so not every project has one). If you update a project's GIF on S3:

```bash
uv run --with pillow python scripts/optimize_project_gifs.py
```

Re-run this after pulling the new GIF locally (start the app once so it downloads to `static/generated/projects/`), then commit whatever lands in `static/optimized_projects/`. This is a manual step by design - it doesn't run automatically.

#### CSS/JS minification

The templates serve `static/css/*.min.css` and `static/js/*.min.js`, not the plain source files. After editing `style.css`, `landing.css`, `static.js`, or `carousel.js`:

```bash
bash scripts/minify_assets.sh
```

Requires `npx` (Node). Commit the regenerated `.min` files alongside your source change - like the two scripts above, this is manual, not automatic.

🛡️ License
This project is licensed under the MIT License.
