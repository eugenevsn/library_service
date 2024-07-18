# Library Service API

A project to develop an online library management system that automates book inventory, user accounts, and borrow tracking with Telegram notifications.
## Setup Instructions

### Clone the repository:
```bash
git clone https://github.com/eugenevsn/library_service.git
cd library_service
```
### Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate # Unix/Mac
.venv\Scripts\activate # Windows
```
### Install dependencies:
```bash
pip install -r requirements.txt
```
### Set up environment variables:
* Create a `.env` file in the project root directory.
* Add the environment variables:

    `SECRET_KEY`<br>
    `TELEGRAM_BOT_TOKEN`<br>
    `TELEGRAM_CHAT_ID`<br>
    `POSTGRES_DB`<br>
    `POSTGRES_USER`<br>
    `POSTGRES_PASSWORD`<br>
    `POSTGRES_HOST`<br>
    `POSTGRES_PORT`<br>
    `CELERY_BROKER_URL`<br>
    `CELERY_RESULT_BACKEND`<br>
    `STRIPE_PUBLIC_KEY`<br>
    `STRIPE_SECRET_KEY`<br>

### Run database migrations:
```bash
python manage.py migrate
```
### Start development server:
```bash
python manage.py runserver
```
### Get access at: 
>http://localhost:8000

## Run with Docker
```bash
docker-compose up
```

## API endpoints
* Book `api/library/books/`
* Borrowing `api/borrowings/`
* Return borrowing `api/borrowings/<int:id>/return/`
* Payments `api/payments/`

User & tokens:

* Get tokens `api/users/token/`
* Refresh token `api/users/token/refresh/`
* Verify token `api/users/token/verify/`
* Register `api/users/register/`
* Get profile `api/users/me/`
