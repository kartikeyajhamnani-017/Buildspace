# LogiRoute – Logistics & Fleet Delivery Backend
LogiRoute is a highly concurrent, robust REST API backend system designed to handle B2B cargo distribution, fleet management, and automated invoicing. Built with a focus on high throughput, strict role-based access control, and domain-driven design principles.

🛠️ Tech Stack & Architecture
Language: Go (Golang)

Web Framework: Gin-Gonic (optimized for minimal memory footprint and fast routing)

Database: MongoDB (utilizing geospatial indexing and embedded document paradigms)

Containerization: Docker & Docker Compose (Multi-stage build optimized for production binaries)

Architecture: Clean Architecture / Domain-Driven Design (Separation of Routes, Controllers, Services, and Repositories)

🚀 Key Features
Fleet & Driver Management: Complete CRUD system for tracking vehicle capabilities, assignments, and availability states.

Multi-State Shipment Tracking: Asynchronous handling of delivery states (Created → Assigned → In-Transit → Delivered).

Geospatial Queries: Leverages MongoDB's 2dsphere indexes to locate the nearest available drivers or warehouses dynamically based on coordinates.

Automated Invoicing Engine: Automated billing computations mapping dimensions, weight thresholds, and travel distance into final operational receipts.

Secure Authentication: JWT-based authentication layered with Role-Based Access Control (RBAC) middleware separating Dispatchers, Drivers, and Client accounts.

📦 Project Structure

├── cmd/
│   └── api/
│       └── main.go          # Application entrypoint
├── internal/
│   ├── config/             #Environmentvariables DB connection setup
│   ├── controllers/         # HTTP request handlers (Gin specific)
│   ├── middleware/          # JWT Auth, Logger, & RBAC interceptors
│   ├── models/              # MongoDB BSON schemas & Go structs
│   ├── repositories/        # Direct database operations layer
│   └── services/            # Core business & dispatch logic code
├── Dockerfile               # Multi-stage production Docker imagedefinition
├── docker-compose.yaml      # Multi-container setup orchestrator (App + MongoDB)
├── go.mod
└── README.md
⚙️ Quick Start
Prerequisites
Docker and Docker Compose installed locally.

Go 1.23+ (optional, if running outside containers).
