#News Platform Project

## Prerequisites
- Python 3.11+
- Docker (optional

## How to build and run with Virtual Environment (venv)
1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
``2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Apply database migrations:
```bash
python manage.py migrate
```
4. Run the development server:
```bash
python manage.py runserver
```

## How to build and run with docker
1. Build the Docker image:
```bash
docker build -t news_platform .
```
2. Run the Docker container:
```bash
docker run -p 8000:8000 news_platform
```

## Environment Variables & Secrets 
- Never commit secret keys or sensitive database credentials  to source control.
- Create a local `.env` file in the root directory to manage your environment variables.
