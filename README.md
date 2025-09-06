A security-focused Python application demonstrating comprehensive software quality practices and security principles. This project implements a minimal-but-complete vertical slice that showcases security practices 

## Project Overview

This application demonstrates:
- **Role-Based Access Control (RBAC)** with SUPER_ADMIN and SYS_ADMIN roles
- **Secure Authentication** with Argon2id password hashing and account lockout
- **Data Encryption** using Fernet (AES + HMAC) for sensitive data
- **Audit Logging** with encrypted logs and suspicious activity detection
- **Backup & Restore** with one-use restore codes
- **Input Validation** with comprehensive whitelist-based validation
- **Clean Architecture** following Hexagonal Architecture principles
