# News Platform Project

A Django REST Framework application designed for managing news publishers, articles, and subscriptions.

## Features
- **Homepage Template**: Rendered HTML homepage listing approved news articles.
- **REST API Endpoints**: Full CRUD for article management.
- **Role-Based Access Control**: Permissions configured for readers, journalists, and editors.
- **Token Authentication**: Endpoints secured via REST framework authentication tokens.

## Setup & Installation Instructions (step-by-step)

Follow these step-by-step instructions to set up and run this project on a fresh machine.

### 1. Clone or Extract the Projet

Open your terminal and naviagte to the extracted project folder:

```bash
cd news_platform_project
```

### 2. Create and Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```
### 3. Install Required Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Database Migrations 

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Execute Test Suite

To verify all views, endpoints, and permissions are operating correctly:

```bash
python manage.py test news_api
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

- Access the HTML Homepage: 'http://127.0.0.1:800/'
- Access the REST API Root: 'http://127.0.0.1:8000/api/articles/'