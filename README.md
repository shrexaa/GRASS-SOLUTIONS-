# 📚 Libra — Library Management System & Dashboard

A beginner-friendly portfolio project combining a library management application with exploratory data analysis (EDA). Built with **Python, Streamlit, SQLite, Pandas, and Plotly**.

> The app inserts synthetic demo records on first launch. They are not real library statistics.

## Features
- Dashboard with book totals, availability, active loans, and overdue counts
- Add, search, edit, and safely delete book records
- Register members and view borrowing activity
- Issue books, set due dates, and record returns
- Automatic availability and overdue calculations
- Category distribution and most-borrowed-title charts
- CSV exports for books, members, and transactions
- SQLite persistence across restarts on the same machine

## Tech stack
| Technology | Use |
|---|---|
| Python | Application logic |
| Streamlit | Interactive web app |
| SQLite | Relational database |
| Pandas | Data processing and EDA |
| Plotly | Interactive charts |

## Project structure
```text
Library_Management_Data_Science/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/config.toml
└── data/README.md
```
`library.db` is generated on first run and intentionally excluded from Git.

## Run on Windows
1. Install Python 3.10+ from https://www.python.org/downloads/ and select **Add Python to PATH**.
2. Extract the ZIP and open a terminal in the project folder.
3. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
4. Activate it in Command Prompt:
   ```bat
   .venv\Scripts\activate
   ```
   PowerShell alternative:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
5. Install packages:
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
6. Run:
   ```bash
   streamlit run app.py
   ```
7. Open the local URL printed in the terminal, usually `http://localhost:8501`.

## Demo walkthrough
1. Add a book under **Book collection**.
2. Register a test member under **Members**.
3. Issue a book and notice available copies decrease.
4. Record the return and notice availability increases.
5. Explore **Data insights** and export a CSV.

## Database design
- `books`: one row per title, total copies, and available copies
- `members`: one row per member
- `transactions`: each loan, linked to a book and member

```text
BOOKS (1) ──── (many) TRANSACTIONS (many) ──── (1) MEMBERS
 book_id           book_id, member_id               member_id
```

## Data Science concepts demonstrated
- Data collection and relational modelling
- Input validation and data quality
- Exploratory data analysis
- Pandas grouping and aggregation
- Category distribution and borrowing frequency
- Availability-rate and overdue-loan analysis
- Interactive data visualization and CSV exports

**Availability rate** = available copies ÷ total copies × 100  
**Copies currently out** = total copies − available copies  
**Overdue loan** = a loan with status `Issued` and a due date earlier than today.

## Push to GitHub
Create an empty repository on GitHub. In the project terminal:
```bash
git init
git add .
git commit -m "Build library management and analytics dashboard"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/Library-Management-Data-Science.git
git push -u origin main
```
Replace `YOUR-USERNAME` with your GitHub username. Authenticate through GitHub's supported login flow. Never commit access tokens, passwords, real member data, or a live database.

## Optional deployment
You can deploy `app.py` using https://share.streamlit.io/. Select your repository and `main` branch. Hosted filesystems may be temporary; local SQLite is for a small demo, not a production multi-user database. Add authentication and a durable hosted database before handling real personal information.

## Limitations / future improvements
- No login or role-based permissions yet
- Demo dataset is synthetic and small
- No fines, reservations, notifications, or barcode scanning
- SQLite suits a small local demo, not a high-concurrency production service
- A forecasting model is a possible extension, but do not claim ML accuracy without implementing and evaluating a model

## Resume description
**Library Management System & Data Analytics Dashboard** — Built a Python web application using Streamlit and SQLite to manage books, members, and issue/return transactions. Used Pandas and Plotly to analyze category distribution, book availability, borrowing frequency, and overdue loans, with CSV export for further analysis.

Only list features you have personally run and verified.

## Suggested repository description
`A Python + Streamlit library management app with SQLite storage, Pandas-based analysis, interactive Plotly charts, and CSV exports.`

## License
For learning and portfolio use. 
