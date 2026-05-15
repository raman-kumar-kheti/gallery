# 🚀 Gallery Monorepo Project Rules

Welcome to the Gallery project. This repository is structured as a monorepo containing everything from the frontend client to backend APIs and AI worker pipelines. 

To ensure a production-ready, maintainable, and highly robust codebase, **all contributors and AI assistants must strictly adhere to the following rules.**

---

## 🏗️ 1. Architecture & General Workflow

### 1.1 End-to-End Context
- **Full Scope Awareness**: This is a monorepo containing multiple interconnected applications (`frontend-web`, `backend-api`, `ai-worker`). Before attempting to solve any issue, you **must** review all relevant parts of the stack to understand the full end-to-end context of the error or feature.
- **Project Documentation**: Every individual project within the monorepo must have its own `README.md` file detailing its specific setup, purpose, and commands.
- **Project Structure**: Always respect and follow the existing project structure and naming conventions when adding anything new. Do not deviate from established architectural patterns.
- **Command Discovery**: For any terminal command, always check the relevant `package.json` file first to see how the command is officially implemented and run.

### 1.2 Logging & Previews
- **No Unnecessary Logs**: Do not write multiple unnecessary lines of `console.log` or throw unhandled errors unless specifically requested by the user. Keep the console clean and strictly for actionable information.
- **No Premature Previews**: Do not use preview tools unless explicitly instructed by the user.

---

## 📘 2. TypeScript & Type Safety

### 2.1 Zero `any` Policy
- **Never use `any`**: The use of the `any` type is strictly prohibited across the entire codebase (frontend, backend, and workers). 
- **Explicit Typing**: You must use proper, accurate TypeScript types, interfaces, or type aliases for all variables, function parameters, return values, and data structures. This is critical so we always know exactly what data structures we are dealing with.

### 2.2 Shared Types
- Keep interfaces and types cleanly scoped. If a type is shared between the backend API and frontend, ensure it is placed in an appropriate shared location or properly exported so both can consume it safely.

---

## 🔐 3. Environment Variables

### 3.1 Strict Access Rules
- **No Direct `process.env`**: You are strictly forbidden from accessing `process.env` directly within any application code (whether it's `frontend-web`, `backend-api`, or `ai-worker`). 
- **Validation**: Environment variables must be accessed through a centralized configuration file that validates and exports them safely (e.g., for `frontend-web` using a schema validator or a dedicated in the app `config.ts` files).

### 3.2 Single Source of Truth & Local Environments
- **Root `.env` Configuration**: All environment variables for the entire project are managed from the root directory. 
- **Adding Variables**: When a new environment variable is added, it **must** be added at the root level `.env` file. The root is the *only* source of truth for the entire monorepo.
- **Local Overrides**: Individual projects may have their own copied `.env.local` files for local development overrides, but these local configurations must always depend on and fall back to the root `.env`.

---

## 🐍 4. Python Environment

### 4.1 Virtual Environments & Setup
- **Mandatory `.venv` Usage**: All Python projects and microservices (e.g., `backend-api`, `ai-worker`) **must** use a local virtual environment (`.venv`). Never install Python dependencies globally or mix them across the host system. Ensure that `.venv` is activated before running or developing Python applications.
- **Setup Requirements**: Every Python project must explicitly include instructions for setting up its `.venv` and installing dependencies within its `README.md`.

---
*By contributing to this repository, you agree to follow these guidelines to maintain a robust, error-free, and scalable production environment.*
