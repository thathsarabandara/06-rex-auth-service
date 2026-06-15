# 🔐 REX-47 Auth Service

> **Repository `06`** · The dedicated identity and access management microservice for the REX-47 platform. Handles secure user registration, JWT lifecycle, and role-based access control.

[![Platform](https://img.shields.io/badge/Platform-Backend-blue)]()
[![Language](https://img.shields.io/badge/Language-JavaScript-F7DF1E?logo=javascript)]()
[![Framework](https://img.shields.io/badge/Framework-Express-000000?logo=express)]()
[![Database](https://img.shields.io/badge/Database-MongoDB-47A248?logo=mongodb)]()
[![Security](https://img.shields.io/badge/Security-JWT%20%7C%20Bcrypt-FF4B4B)]()

---

## 📋 Table of Contents

- [Overview](#-what-is-this-repository)
- [Architecture](#-architecture)
- [Features](#-features)
- [Getting Started](#-getting-started)
- [Authentication Flow](#-authentication-flow)
- [Database Schema](#-database-schema)
- [Dependencies](#-dependencies)
- [Related Repositories](#-related-repositories)

---

## 🧭 What Is This Repository?

This is the **central authentication authority** for the entire REX-47 ecosystem. All login requests, token validations, and permission checks are processed here before the API Gateway allows requests to touch the robot's core systems.

**Key Highlights:**
- ✅ **Stateless JWT Auth:** Issues signed JSON Web Tokens for scalable, stateless session management across microservices.
- ✅ **Role-Based Access Control (RBAC):** Differentiates between 'Admin', 'Operator', and 'Viewer' privileges.
- ✅ **Secure Password Hashing:** Utilizes Bcrypt for robust password salting and hashing.
- ✅ **OTP & Recovery Flows:** Built-in email integration for password resets and identity verification.

---

## 🏗️ Architecture

### Directory Structure

```
06-rex-auth-service/
├── src/
│   ├── config/               ← Environment variables and DB connection logic
│   ├── controllers/          ← Business logic for auth endpoints
│   ├── middlewares/          ← JWT validation and role-checking guards
│   ├── models/               ← Mongoose schemas (User, Role, Token)
│   ├── routes/               ← Express route definitions (/register, /login)
│   ├── utils/                ← Email senders, OTP generators, Token signers
│   └── index.js              ← Service entry point
├── .env.example              ← Environment template file
├── docker-compose.yml        ← Local development DB/service definitions
├── Dockerfile                ← Container build instructions
├── package.json              ← Dependencies and scripts
└── README.md                 ← This documentation
```

---

## 🎨 Features

### 👤 **User Management**

| Feature | Description |
|---------|-------------|
| **Registration** | Secure account creation with email validation and strict password requirements. |
| **Profile Management** | Endpoints to update metadata, avatars, and contact information. |
| **Account Locking** | Security measure preventing brute force after multiple failed login attempts. |

### 🔑 **Token & Session Management**

| Feature | Description |
|---------|-------------|
| **JWT Generation** | Issues short-lived Access Tokens and long-lived Refresh Tokens. |
| **Token Invalidation** | Robust logout mechanism that blacklists compromised or active tokens. |
| **Middleware Guards** | Reusable middleware ensuring `verifyToken` and `isAdmin` checks pass. |

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** ≥ 18.x
- **MongoDB** (Local instance or Atlas URI)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/thathsarabandara/06-rex-auth-service.git
cd 06-rex-auth-service

# 2. Install dependencies
npm install

# 3. Configure environment variables
cp .env.example .env
```

### Environment Configuration

Ensure you have a strong JWT Secret configured in your `.env` file:

```env
PORT=5001
NODE_ENV=development

# Database
MONGO_URI=mongodb://localhost:27017/rex-auth

# Security
JWT_SECRET=your_super_secret_key_here
JWT_EXPIRES_IN=1h
REFRESH_TOKEN_SECRET=your_refresh_secret
```

### Running the Application

```bash
# Development mode with Nodemon
npm run dev

# Production mode
npm start
```

---

## 🔐 Authentication Flow

1. **Client Request:** The web or mobile app sends credentials to the API Gateway.
2. **Proxy:** The API Gateway proxies the request to the Auth Service.
3. **Validation:** The Auth Service verifies the Bcrypt hash against the database.
4. **Token Issuance:** If valid, an Access Token (JWT) is returned to the client.
5. **Subsequent Requests:** The client attaches the JWT in the `Authorization: Bearer <token>` header for all future requests to the Robot or Telemetry services.

---

## 📦 Dependencies

### Core
- `express` — Web framework
- `mongoose` — MongoDB object modeling tool

### Security
- `bcryptjs` — Password hashing and salting
- `jsonwebtoken` — Token signing and verification
- `express-validator` — Request body sanitization

---

## 🔗 Related Repositories

- [05-rex-api-gateway](../05-rex-api-gateway) — Proxies traffic to this service.
- [03-rex-web-dashbaord](../03-rex-web-dashbaord) — The frontend interface utilizing these auth flows.
- [04-rex-mobile-app](../04-rex-mobile-app) — The mobile interface utilizing these auth flows.
