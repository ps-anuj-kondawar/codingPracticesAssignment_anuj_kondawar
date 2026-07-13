# Employee Management Console Application

A command-line based Employee Management System (EMS) written in Python, designed following clean code principles and programming best practices.

---

## 🛠️ Features Implemented

### Core Features
- **Add Employee Details**: Prompts for Employee ID, Name, Email, Department, Designation, and Joining Date.
- **View All Employees**: Displays all employee details in a cleanly aligned ASCII table format.
- **Search Employee**: Search for a specific employee by ID (case-insensitive).
- **Update Details**: Update details for an existing employee. Pressing `Enter` keeps the current value.
- **Delete Employee**: Remove an employee record after a safety confirmation prompt.
- **Exit**: Exits the program safely and gracefully.

### Bonus Features
- **Sorting**: View employees sorted by Name in Ascending (A-Z) or Descending (Z-A) order.
- **Filtering**: Filter and view employees belonging to a specific department.
- **Duplicate ID Prevention**: The application prevents adding an employee with an ID that already exists.
- **Data Persistence**: Employee records are saved in JSON format to `employees.json` automatically when changes occur.
- **Unit Tests**: Full unit test coverage for business logic using Python's standard `unittest` framework.

---

## 📐 Best Practices Followed

1. **Meaningful Naming Conventions**: Used clear, descriptive names for all classes, methods, and variables (e.g., `EmployeeConsoleApp`, `validate_email`, `employees.json`).
2. **Single Responsibility Principle (SRP)**:
   - `Employee`: Defines the data model and structural validation logic.
   - `EmployeeService`: Manages business operations and data persistence.
   - `EmployeeConsoleApp`: Handles user input, output formatting, and CLI state.
3. **Avoid Duplicate Code**: Reusable input collection helper method (`prompt_input`) with validation loops to handle prompt loops cleanly.
4. **Input Validation**:
   - **ID**: Checked for non-empty input and duplicate prevention.
   - **Name**: Checked for non-empty input.
   - **Email**: Verified using standard email regular expressions.
   - **Joining Date**: Enforced strict `YYYY-MM-DD` date parsing and formatting.
5. **Error Handling**: Gracefully handles incorrect user choices, invalid file formats, and `KeyboardInterrupt` (`Ctrl+C` or `EOFError`) during text entry without crashing the application.
6. **No Hardcoded Constants**: Colors and repeated UI values are defined as clear constants.

---

## 🚀 How to Run the Application

Ensure you have **Python 3.3+** installed.

### Run the App
From the root directory, execute:
```bash
python main.py
```

### Run the Unit Tests
To execute all the validation and business logic test cases:
```bash
python -m unittest discover -s tests
```

---

## 💾 Data Storage & Sample Seed Data

The application stores records in a local file named `employees.json`. This file is loaded from and saved to the **working directory** where the command is executed. It is portable and directory-independent.

To test the application with pre-existing data (e.g. for evaluation/grading):
1. Create a new file named `employees.json` in the root folder of the project.
2. Copy and paste the following sample data array into it:
```json
[
    {
        "employee_id": "EMP001",
        "name": "Alice Smith",
        "email": "alice@example.com",
        "department": "Engineering",
        "designation": "Tech Lead",
        "joining_date": "2026-07-01"
    },
    {
        "employee_id": "EMP002",
        "name": "Bob Miller",
        "email": "bob@example.com",
        "department": "Engineering",
        "designation": "Developer",
        "joining_date": "2026-07-02"
    },
    {
        "employee_id": "EMP003",
        "name": "Charles Brown",
        "email": "charlie@example.com",
        "department": "HR",
        "designation": "Recruiter",
        "joining_date": "2026-07-03"
    }
]
```
3. Run the app (`python main.py`) and the records will load automatically!

---

## 📸 Application Screenshots

### 1. Main Menu Screen
Shows the starting page and clean interface of the system:
![Main Menu Screen](screenshots/first_screen.png)

### 2. Adding an Employee (with Validation Check)
Demonstrates input processing and successful validation:
![Add Employee Flow](screenshots/emp_add.png)

### 3. Displaying and Sorting/Filtering Records
Shows the custom-formatted, auto-scaling data table, sorting, and department-filtering in action:
![Employee Table Grid, Sorting, and Filtering](screenshots/sorting.png)

### 4. Search and Selective Update
Shows searching a record and updating specific fields while leaving others unchanged:
![Searching and Updating Employee](screenshots/search_update.png)

### 5. Deletion & Safety Confirmation
Shows the confirmation prompt before removing a record:
![Deleting Employee](screenshots/delete.png)
