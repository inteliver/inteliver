<p align="center">
  <a href="https://github.com/inteliver/inteliver"><img src="https://raw.githubusercontent.com/inteliver/inteliver/main/src/inteliver/assets/images/inteliver-logo.svg" alt="inteliver logo"></a>
</p>

<p align="center">
    <em>inteliver, high performance, ready for production, image management.</em>
</p>

<p align="center">
<b>Opensource</b> alternative to <a href="https://cloudinary.com/">cloudinary<a>
</p>

---

[![Build Status](https://img.shields.io/github/actions/workflow/status/inteliver/inteliver/docker-publish.yml)](https://github.com/inteliver/inteliver/actions/workflows/docker-publish.yml)
[![Maintainability](https://api.codeclimate.com/v1/badges/85b24e0a5466be54852f/maintainability)](https://codeclimate.com/github/inteliver/inteliver/maintainability)
[![GitHub language](https://img.shields.io/github/languages/top/inteliver/inteliver)](https://github.com/inteliver/inteliver)
![GitHub License](https://img.shields.io/github/license/inteliver/inteliver)
[![PyPI Version](https://img.shields.io/pypi/v/inteliver)](https://pypi.org/project/inteliver/)
[![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/inteliver/inteliver)](https://github.com/inteliver/inteliver)

<!-- [![Python Version](https://img.shields.io/pypi/pyversions/inteliver)](https://pypi.org/project/inteliver/) -->



## inteliver Overview

<a href="https://inteliver.github.io/inteliver/" target="_blank">inteliver</a> is an **open-source** alternative to <a href="https://cloudinary.com/" target="_blank">cloudinary</a>.

inteliver is an **image management platform** offering programmable media solutions.

### 🚀 Key Features

### 🖼️ Image Management Features
- 📝 **On-the-Fly Image Modification**: Resize, crop, sharpen, blur, pixelate, and more in real time with caching.
- 🤖 **A.I. and Image Information**: Detect objects and faces in your images and modify them semantically.
- 📉 **Real-Time Image Compression**: Reformat and compress images in various formats efficiently.
- 😎 **Self-Host**: **self-host** inteliver using a simple, all-inclusive **Docker Compose**.

### ⚙️ Async Backend APIs
- ⚡ **[FastAPI](https://fastapi.tiangolo.com)** as the ASGI web server for the backend API.
- 🔍 **[Pydantic](https://docs.pydantic.dev)** for data validation and schemas.
- 💾 **[PostgreSQL](https://www.postgresql.org)** as the SQL database.
- 🐦 **[alembic](https://alembic.sqlalchemy.org/)** as lightweight database migration tool
- ☕ **[SQLAlchemy](https://www.sqlalchemy.org/)** as the main ORM.
- ✅ Comprehensive testing with **[Pytest](https://pytest.org)**.


### 🛡️ Built-in User Management
- 🔑 **JWT** (JSON Web Token) for authentication.
- 🔒 Secure password hashing by default.
- 🎛️ Role-based access control with admin and user levels.
- 📫 Email-based password recovery.

### 🗄️ Storage
- ☁️ **[MinIO](https://min.io/)** as cloud-native object storage (compatible with any **S3** storage).
- 🔍 Automatic image type detection.
- 📤 Simple, intuitive upload and retrieval endpoints for image data.

### 📦 Deployment
- 🐳 **[Docker](https://www.docker.com)** for containerization.
- 📦 **[Docker Compose](https://www.docker.com)** for development and production workflows.
- 🔧 **[Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)** for managing environment variables across development, staging, and production environments.
- 📞 **[Traefik](https://traefik.io)** as a reverse proxy and load balancer.
- 🏭 Continuous Integration (CI) and Continuous Deployment (CD) with GitHub Actions.

---

## ▶️ Watch Introduction Video 

This introductory video explains what Inteliver is, how it operates, and how it can enhance your image management processes.

<figure markdown="span">
  <a href="https://www.youtube.com/watch?v=8hEdIEvt7_E" target="_blank">
    <img 
      src="https://raw.githubusercontent.com/inteliver/inteliver/main/docs/assets/inteliver-introduction-video-snapshot.svg" alt="inteliver Introduction Video"
      style="display: block; margin: 0 auto; border-radius: 16px;"
    />
  </a>
</figure>

---
