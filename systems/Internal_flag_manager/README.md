# 📌 Internal Flag Manager

## 🧩 Overview

**Internal Flag Manager** is a Spring Boot-based RESTful CRUD application designed to manage internal feature flags within a system.

It enables controlled activation/deactivation of application features, making it useful for:

- Feature rollouts  
- Controlled experiments  
- Operational toggles  
- Internal configuration management  

The application uses PostgreSQL for persistent storage and follows clean layered architecture principles.

---

## ⚙️ Tech Stack

- **Java 17+**
- **Spring Boot**
- **Spring Data JPA (Hibernate)**
- **PostgreSQL**
- **Maven**
- REST APIs

---

## 🏗 Architecture

The project follows a standard layered architecture:

Controller → Service → Repository → Database

- **Controller Layer** – Exposes REST endpoints  
- **Service Layer** – Contains business logic  
- **Repository Layer** – Handles DB interactions via JPA  
- **PostgreSQL** – Persistent data storage  

---

## 🗄 Database Configuration

The application uses environment variables for database credentials — nothing sensitive is hardcoded in `application.properties`, which reads `${DB_URL}`, `${DB_USER}` and `${DB_PASSWORD}` at startup.

### Required Environment Variables

```bash
DB_URL=jdbc:postgresql://localhost:5432/FeatureDB
DB_USER=postgres
DB_PASSWORD=your_password
```

A template is provided at `Internal_flag_manager/db.env.example` — copy it to `db.env` and fill in your own values (`db.env` is git-ignored).

---

## 🔌 API Endpoints

Base path: `/feature`

| Method | Path | Description |
|---|---|---|
| POST | `/feature/add` | Create a new feature flag |
| GET | `/feature/listall` | List all feature flags |
| PUT | `/feature/toggle/{id}` | Toggle a flag's active status |
| DELETE | `/feature/delete/{id}` | Delete a single flag |
| DELETE | `/feature/deleteall` | Delete all flags |

There's also a server-rendered dashboard at `/` (Thymeleaf) for creating, toggling, and deleting flags from the browser without calling the API directly.

---

## 🚀 Get Started

### Prerequisites

* Java 17+
* PostgreSQL (running locally, or via Docker)
* (Optional) Docker, if you'd rather containerize the app than install Java/Maven

### 1. Clone the repo

```bash
git clone https://github.com/kartikeyajhamnani-017/myprojects-repo
cd myprojects-repo/Minor-projects/Internal_flag_manager/Internal_flag_manager
```

### 2. Configure secrets

```bash
cp db.env.example db.env
```

Edit `db.env` and set `DB_PASSWORD` to match your local Postgres setup.

### 3. Create the database

```sql
CREATE DATABASE "FeatureDB";
ALTER USER postgres WITH PASSWORD 'the_password_you_put_in_db.env';
```

The `feature_flag` table is created automatically on first run (`spring.jpa.hibernate.ddl-auto=update`).

### 4. Run the app

**Option A — Maven wrapper (recommended, no local Maven install needed):**

```bash
# Windows (PowerShell): load db.env into the current session first
Get-Content db.env | ForEach-Object { if ($_ -match '^([^#=]+)=(.*)$') { [Environment]::SetEnvironmentVariable($matches[1], $matches[2]) } }
.\mvnw.cmd spring-boot:run

# macOS/Linux:
export $(grep -v '^#' db.env | xargs)
./mvnw spring-boot:run
```

**Option B — Docker:**

```bash
docker build -t internal-flag-manager .
docker run --env-file ./db.env -p 8000:8000 internal-flag-manager
```

> With Docker, set `DB_URL` in `db.env` to use `host.docker.internal` instead of `localhost` so the container can reach Postgres on your host machine.

### 5. Try it out

* Dashboard UI: `http://localhost:8000/`
* REST API: `http://localhost:8000/feature/listall`