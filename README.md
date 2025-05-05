# Service Ticket Management System

A Flask-based web application for managing service tickets, customers, and mechanics. This project allows users to create, retrieve, and manage service tickets while associating them with customers and mechanics.

## Features

- **Create Service Tickets**: Add new service tickets with details like service date, description, customer, and associated mechanics.
- **Retrieve Service Tickets**: View all service tickets with customer and mechanic details.
- **Customer Management**: Associate service tickets with customers.
- **Mechanic Management**: Assign multiple mechanics to a service ticket.

## Technologies Used

- **Backend**: Flask (Python)
- **Database**: SQLAlchemy (with SQLite or other supported databases)
- **Serialization**: Marshmallow for schema validation and serialization
- **ORM**: Flask-SQLAlchemy

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd service_ticket
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


