# SmartPenny

SmartPenny is a responsive student expense tracker built with Flask. It helps users record income and expenses, explore spending by category, compare activity over time, and understand their overall financial position through a clean dashboard.

## Key Features

- **Secure account management**
  - Create an account, sign in, and sign out
  - Passwords are hashed with Werkzeug
  - Flask-Login protects private routes
  - CSRF protection is enabled for forms and account actions

- **Income and expense tracking**
  - Add, edit, and delete transactions
  - Store amount, date, type, category, and an optional note
  - Validate positive amounts and expense categories
  - Search transactions by description, category, or type

- **Powerful transaction history**
  - Filter by month or view all-time activity
  - Sort by date, category, or amount
  - Paginate large transaction histories
  - Preserve filters while navigating pages and sorting

- **Interactive dashboard**
  - View all-time balance
  - View period income and expenses
  - Explore spending with a doughnut chart
  - Compare monthly income and expenses
  - Track end-of-month balance for the last six months
  - Review recent transactions and top spending categories

- **Category insights**
  - See spending totals for each default category
  - View transaction counts and percentage share
  - Filter category reports by month

- **Modern user experience**
  - Responsive desktop and mobile layout
  - Light and dark themes
  - Theme preference saved in the browser
  - Indian rupee formatting
  - Accessible labels and transaction controls

- **Database tooling**
  - SQLAlchemy data models
  - Flask-Migrate and Alembic migrations
  - Automatic seeding of default expense categories

## Tech Stack

| Layer | Technology |
| --- | --- |
| Backend | Python, Flask |
| Database | SQLAlchemy, PostgreSQL or SQLite |
| Authentication | Flask-Login, Werkzeug password hashing |
| Forms and security | Flask-WTF, CSRF protection |
| Migrations | Flask-Migrate, Alembic |
| Frontend | Jinja2, HTML, CSS, JavaScript |
| Charts | Chart.js |

## Project Structure

```text
student-expense-tracker/
├── app.py                  # Flask application factory and startup
├── config.py               # Environment-based configuration
├── extensions.py           # Database, auth, migrations, and CSRF extensions
├── models.py               # User, Category, and Transaction models
├── utils.py                # Period, totals, formatting, and chart calculations
├── requirements.txt        # Python dependencies
├── migrations/             # Alembic database migrations
├── routes/
│   ├── auth.py             # Sign-up, sign-in, and sign-out
│   ├── dashboard.py        # Dashboard totals and chart data
│   ├── transactions.py     # Transaction CRUD, search, sorting, pagination
│   └── categories.py       # Category spending report
├── static/
│   ├── css/                # Application styles and themes
│   └── js/                 # Theme and dashboard JavaScript
└── templates/
    ├── base.html           # Shared layout and navigation
    ├── auth.html           # Sign-up and sign-in page
    ├── dashboard.html      # Dashboard and charts
    ├── transactions.html   # Transaction history and editor
    ├── categories.html     # Category spending report
    └── _*.html             # Reusable month and pagination components
```

## Getting Started

### Prerequisites

- Python 3.10 or newer
- PostgreSQL, or SQLite for a local setup
- A virtual environment manager

### 1. Clone the repository

```bash
git clone https://github.com/mrudularane16/student_expense_tracker.git
cd student_expense_tracker
```

### 2. Create and activate a virtual environment

**Windows**

```powershell
python -m venv venv
venv\Scripts\activate
```

**macOS or Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=replace-with-a-long-random-secret
DATABASE_URL=sqlite:///instance/student_expense_tracker.db
```

For PostgreSQL:

```env
SECRET_KEY=replace-with-a-long-random-secret
DATABASE_URL=postgresql://postgres:password@localhost:5432/expense_tracker
```

The application also uses the PostgreSQL URL above as its default if `DATABASE_URL` is not set. Always use a strong, unique `SECRET_KEY` outside local development.

### 5. Create or upgrade the database

Apply the included migration:

```bash
flask --app app db upgrade
```

Default expense categories are seeded automatically when the categories table is available and empty.

### 6. Run the application

```bash
python app.py
```

Open `http://127.0.0.1:5000` in a browser.

## Default Categories

SmartPenny creates these expense categories automatically:

- Food
- Transportation
- Shopping
- Bills
- Entertainment
- Healthcare
- Education

## How the Main Features Work

### Transaction history

The transaction page supports keyword search, income/expense filtering, month selection, date/category/amount sorting, and pagination. The add and edit form shares the same validation flow to keep transaction data consistent.

### Dashboard analysis

Dashboard totals can be filtered by month while the current balance remains all-time. Chart.js renders the category, monthly comparison, and balance trend visualizations in light or dark mode.

### Period navigation

The month picker lists available transaction months plus the current month. Users can move to a previous or next month or switch to all-time activity.

### Database migrations

Use Flask-Migrate to manage schema changes:

```bash
flask --app app db migrate -m "describe the change"
flask --app app db upgrade
```

## Security Notes

- Use HTTPS when deploying the application.
- Set a strong `SECRET_KEY` through environment variables.
- Store database credentials outside source control.
- Do not commit `.env`, virtual environments, temporary databases, or private database files.
- CSRF protection is applied to authenticated forms and mutation actions.

## Running in Production

For deployment, use a production WSGI server instead of Flask's debug server. Set `SECRET_KEY` and `DATABASE_URL` securely, run migrations, and configure HTTPS.

Example package:

```bash
pip install gunicorn
gunicorn "app:app"
```


