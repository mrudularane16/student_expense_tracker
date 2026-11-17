# SmartPenny

SmartPenny is a lightweight Flask web application designed for students to track day-to-day spending, monitor income, and stay on top of their financial habits. It helps users log transactions, categorize expenses, and review a clear summary of their financial health from a single dashboard.

## Features

- User authentication with sign up and sign in
- Add, edit, and delete income and expense records
- Expense category tracking for common student spending areas
- Dashboard with current balance, total income, and total expenses
- Category-wise spending breakdown and visual progress bars
- Search and filter transactions by keyword or type
- Clean, responsive interface for personal finance management

## Tech Stack

- Python 3
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Jinja2 templates
- HTML, CSS, and JavaScript
- PostgreSQL (default configuration) or SQLite for local development

## Project Structure

```text
student-expense-tracker/
├── app.py                  # App factory and entry point
├── config.py               # Application configuration
├── extensions.py           # Flask extensions instance
├── models.py               # Database models
├── requirements.txt        # Python dependencies
├── utils.py                # Utility functions for finance calculations
├── instance/               # Local database files
├── routes/                 # Blueprints for auth, dashboard, transactions, categories
├── static/                 # CSS and JavaScript assets
├── templates/              # HTML templates
├── README.md               # Project documentation
└── .env.example            # Optional example environment file (if added locally)
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/student-expense-tracker.git
cd student-expense-tracker
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

- Windows:
  ```bash
  .venv\Scripts\activate
  ```
- macOS/Linux:
  ```bash
  source .venv/bin/activate
  ```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root and set the required variables:

```env
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///instance/student_expense_tracker.db
```

You can also use PostgreSQL if preferred:

```env
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://postgres:root@localhost:5432/expense_tracker
```

> The project defaults to PostgreSQL in `config.py`, but SQLite is easier for local development and testing.

### 5. Run the application

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000/
```

## How It Works

### Authentication

Users can create an account, sign in, and maintain a personal financial profile. The app uses Flask-Login to manage authenticated sessions securely.

### Transactions

Each transaction includes:

- type: income or expense
- amount
- category
- date
- description

Expense entries are tied to categories such as Food, Transportation, Shopping, Bills, Entertainment, Healthcare, and Education.

### Dashboard

The dashboard provides a quick snapshot of:

- current balance
- total income
- total expenses
- recent transactions
- spending by category

### Categories and Insights

The categories page aggregates spending data to show how much each category contributes to a user’s total expenses.

## Default Expense Categories

The app seeds the following categories automatically:

- Food
- Transportation
- Shopping
- Bills
- Entertainment
- Healthcare
- Education






