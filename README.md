
# Lockzilla

## Overview

Lockzilla is a secure password manager that helps users store, manage, and protect passwords across multiple accounts. It addresses common challenges in password management by providing a centralized platform with strong encryption, password health monitoring, and multi-user support.

---

## Key Features

* Add, update, and delete passwords securely.
* Password strength analysis using “pwned” API to detect compromised passwords.
* Generate strong, random passwords to reduce weak or reused credentials.
* Multi-user support for teams or families.
* Copy-to-clipboard functionality for safe and convenient password usage.
* Intuitive interface for easy password management.

---

## Technology Stack

* **Backend Framework:** Flask
* **Database Management:** SQLite3
* **Security:** Werkzeug for encryption and SHA hashing
* **Frontend:** HTML, CSS, JavaScript (via Flask templates)
* **External APIs:** “pwned” API for password breach checks

---

## How It Works

1. **User Authentication:** Handles login and registration securely with hashed passwords.
2. **Password Storage:** Encrypts and stores credentials in SQLite3.
3. **Password Management:** Users can add, edit, delete, and view passwords.
4. **Security Features:**

   * SHA encryption ensures passwords are never stored in plaintext.
   * Password generator for strong credentials.
   * Password health check to detect vulnerabilities.
5. **Clipboard Copy:** Allows secure copying of passwords without exposing them.

---

## Getting Started

1. Clone the repository:

   ```bash
   git clone <repository-url>
   ```
2. Install required Python packages:
3. Run the application:

   ```bash
   python app.py
   ```
4. Access the application via your browser at `http://localhost:5000`.

---

## Modules Overview

* **User Management:** Registration, login, and session handling.
* **Password Dashboard:** View, add, edit, and delete passwords.
* **Password Health:** Check if passwords are breached or weak.
* **Password Generator:** Create strong, random passwords.

---

## License

Educational use; can be adapted for personal or team password management workflows.
