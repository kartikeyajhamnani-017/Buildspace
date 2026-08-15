# LedgerEz – Secure Digital Ledger (Spring Boot + React)

A full-stack fintech-style ledger application built with Spring Boot (JWT Security) and React, implementing stateless authentication and production-structured backend architecture.

This project demonstrates secure REST API design, Spring Security internals, and frontend-backend integration.

---

## 🔐 Key Highlights

- Stateless JWT Authentication  
- Spring Security (Custom AuthenticationProvider)  
- BCrypt password hashing  
- CORS-secured API (Frontend on port 3000)  
- Role-ready architecture (extensible)  
- Clean layered backend structure  
- Modern React UI with protected routes  

---

## 🏗 Tech Stack

### Backend

- Java 17  
- Spring Boot 3  
- Spring Security  
- JWT  
- JPA / Hibernate  
- PostgreSQL  

### Frontend

- React  
- React Router  
- Context API  
- Axios  

---

## 🧠 Architecture
```bash
React (3000)
↓
Spring Boot API (9000)
↓
PostgreSQL
```


### Authentication Flow


* Login → AuthenticationManager → JWT → Client stores token → Protected API access

---

## 🚀 Features

- User Registration & Login  
- Wallet Management  
- Contact Management  
- Transaction Tracking  
- Dashboard Foundation  
- Protected API Endpoints  
- Stateless Session Policy  

## 🎯 What I learned 

- Deep understanding of Spring Security configuration  
- Manual AuthenticationManager usage  
- Custom DaoAuthenticationProvider wiring  
- JWT filter implementation  
- Secure frontend-backend integration  
- Production-ready project structure  

---

## 🚀 Get Started

No secrets are hardcoded in this repo — the backend reads `DB_URL`, `DB_USER`, `DB_PASSWORD` and `JWT_SECRET` from environment variables, with `LedgerEzBackend/db.env.example` as the template.

### Prerequisites

* Java 17+
* PostgreSQL (running locally, or via Docker — see step 3)
* Node.js 18+ and npm
* (Optional) Docker, if you'd rather containerize the backend than install Java/Maven

### 1. Clone the repo

```bash
git clone https://github.com/kartikeyajhamnani-017/myprojects-repo
cd myprojects-repo/Minor-projects/LedgerEz
```

### 2. Configure backend secrets

```bash
cd LedgerEzBackend
cp db.env.example db.env
```

Edit `db.env` and set your own `DB_PASSWORD` and a random `JWT_SECRET` (any long random string — e.g. run `openssl rand -hex 32` or `python -c "import secrets; print(secrets.token_hex(32))"`). `db.env` is git-ignored, so your values stay local.

### 3. Create the database

Make sure PostgreSQL is running, then create a database and user matching what you put in `db.env` (default DB name is `LedgerEzDB`, default user `postgres`):

```sql
CREATE DATABASE "LedgerEzDB";
ALTER USER postgres WITH PASSWORD 'the_password_you_put_in_db.env';
```

Tables are created automatically on first run (`spring.jpa.hibernate.ddl-auto=update`).

### 4. Run the backend

**Option A — Maven wrapper (recommended, no local Maven install needed):**

```bash
# from LedgerEzBackend/, with db.env values exported as real env vars
# Windows (PowerShell):
Get-Content db.env | ForEach-Object { if ($_ -match '^([^#=]+)=(.*)$') { [Environment]::SetEnvironmentVariable($matches[1], $matches[2]) } }
.\mvnw.cmd spring-boot:run

# macOS/Linux:
export $(grep -v '^#' db.env | xargs)
./mvnw spring-boot:run
```

**Option B — Docker:**

```bash
docker build -t ledgerez-backend .
docker run --env-file ./db.env -p 9000:9000 ledgerez-backend
```

> With Docker, `DB_URL` in `db.env` uses `host.docker.internal` so the container can reach Postgres running on your host machine.

The backend is now live at `http://localhost:9000/api/v1/`.

### 5. Run the frontend

```bash
cd ../ledgerezfrontend
npm install
npm start
```

Opens at `http://localhost:3000`, already wired to talk to the backend on port 9000.

### 6. Try it out

* Register a user at `/register`, log in at `/login`
* Add funds to your wallet, add a contact, send money between two registered accounts
* Download a PDF transaction statement from the Transactions page

---