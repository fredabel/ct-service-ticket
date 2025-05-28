# Service Ticket Management System

A Flask-based web application for managing customers, mechanics, service tickets, serialized parts, and inventory for an automotive service business. This project allows users to create, retrieve, and manage service tickets while associating them with customers and mechanics.


## Features
- **User Authentication**: JWT-based login for customers and mechanics.
- **Service Ticket Management**: Create, edit, assign mechanics/parts, and delete tickets.
- **Inventory Management**: Track serialized parts and part descriptions.
- **Rate Limiting & Caching**: Prevent abuse and improve performance.
- **Comprehensive API**: CRUD operations for all major resources.

## Technologies Used
- **Backend**: Flask (Python)
- **Database**: SQLAlchemy (with SQLite or other supported databases)
- **Serialization**: Marshmallow for schema validation and serialization
- **ORM**: Flask-SQLAlchemy
- **Authentication**: JWT (python-jose)
- **Rate Limiting**: Flask-Limiter
- **Caching**: Flask-Caching


## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/fredabel/ct-service-ticket.git
   cd ct-service-ticket
2. **Set Up a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
3. **Install dependencies**:
   ```bash
    pip install -r requirements.txt
4. **Set Up the Database**:
   - Create a database in MySQL:
     ```sql
     CREATE DATABASE service_shop_db;
     ```
   - Alternatively, use a preferred database name:
     ```sql
     CREATE DATABASE <your_database_name>;
     ```
5. **Update the [SQLALCHEMY_DATABASE_URI] ariable in [config.py]**
   ```python
     SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://<user>:<password>@localhost:3306/<database_name>'
     ```
     Replace `<user>`, `<password>`, and `<database_name>` with your MySQL username, password, and the name of the database you created.
6. **Run the application**
   ```python 
      python app.py
   ```
7. **Access the application at http://127.0.0.1:5000.**

## Testing
This project includes a suite of unittests.  
To run all tests:

```sh
python -m unittest discover tests
```

API Documentation
Interactive API docs are available via Swagger UI.
After starting the server, visit: http://127.0.0.1:5000/api/docs/
