# Secure Task Management Application (secure-task-app)

An implementation of an injection-free, role-based Task Management web application built using secure-by-design architectural paradigms. This project serves as the primary assessment milestone for **IKB 21503: Secure Software Development** at UniKL MIIT.

---

## 1. Project Description
The **Secure Task Management Application** is a collaborative system for managing workflows, task assignments and tracking progress securely. This application is build using the Python **Django** framework and focuses on addressing OWASP Top 10 vulnerabilities. 

Rather than relying purely on passive framework automation, this system actively integrates robust input sanitization pipelines, strict multi-tenant data boundaries, structural session security, and continuous third-party vulnerability remediation to guarantee the confidentiality, integrity, and availability of system state profiles.

---

## 2. Installation Steps

Follow these sequential procedures to deploy the development environment locally:

### Prerequisites
* Python 3.10+
* Git Version Control System

### Step-by-Step Setup
1. **Clone the Project Repository:**
   ```bash
   git clone [https://github.com/denniiyyy/task_management.git](https://github.com/denniiyyy/task_management.git)
   cd task_management
   ```
2. Initialize Local Virtual Environment:
```bash
python -m venv venv
```
3. Activate Environment Context:
```bash
venv\Scripts\activate
```
4. Provision Third-Party Modules:
```bash
pip install -r requirements.txt
```
5. Execute Relational Schema Migrations:
```bash
python manage.py migrate
```
6. How to Run the App:
```bash
venv\Scripts\activate
```
7. Confirm your virtual environment context remains active:
```bash
venv\Scripts\activate
```
8. Launch the local runtime daemon:
```bash
python manage.py runserver
```
