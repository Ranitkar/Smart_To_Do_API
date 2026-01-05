# Smart_To_Do_API
A robust REST API for task management built with Python (FastAPI) and MongoDB. Features secure JWT authentication, asynchronous database operations, and automatic Swagger documentation.
**Smart ToDo API** is a high-performance backend system designed to manage user tasks securely and efficiently. Built with the modern **FastAPI** framework, it leverages asynchronous **MongoDB** queries to handle data and implements industry-standard **JWT (JSON Web Token)** authentication for security.

This project is fully documented with interactive Swagger UI, making it easy to test and integrate.

---

## ✨ Features

* **⚡ High Performance:** Built on Starlette and Pydantic (FastAPI) for blazingly fast execution.
* **🔐 Secure Authentication:** Stateless user authentication using **JWT** and **Bcrypt** password hashing.
* **🗄️ NoSQL Integration:** Asynchronous database operations using **MongoDB** and the **Motor** driver.
* **📑 Interactive Documentation:** Automatic generation of **Swagger UI** and **Redoc** for testing endpoints.
* **🛡️ Data Validation:** Robust request validation using **Pydantic** models.
* **🔄 CRUD Operations:** Full support for Creating, Reading, Updating, and Deleting tasks.

---

## 🛠️ Tech Stack

### Core Framework
* **Python 3.9+**
* **FastAPI:** The web framework for building the API.
* **Uvicorn:** ASGI server for production.

### Database
* **MongoDB Atlas:** Cloud-hosted NoSQL database.
* **Motor:** Asynchronous Python driver for MongoDB.

### Security
* **Python-Jose:** For generating and verifying JSON Web Tokens.
* **Passlib (Bcrypt):** For secure password hashing.
* **OAuth2:** For handling bearer token flows.

---

## ⚙️ Installation & Setup

Follow these steps to run the API locally.

### Prerequisites
* Python installed on your machine.
* A MongoDB connection string (local or MongoDB Atlas).
