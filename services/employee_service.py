import json
import os
from typing import List, Optional, Tuple
from models.employee import Employee

class EmployeeService:
    """Handles business logic for employee management, including storage, CRUD operations, sorting, and filtering."""

    def __init__(self, db_path: str = "employees.json"):
        self.db_path = db_path
        self.employees: List[Employee] = []
        self.load_employees()

    def load_employees(self) -> None:
        """Loads employees from the JSON database file. Handles empty or corrupt files gracefully."""
        if not os.path.exists(self.db_path):
            self.employees = []
            return
        
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.employees = [Employee.from_dict(item) for item in data]
                else:
                    self.employees = []
        except (json.JSONDecodeError, OSError, KeyError):
            # If the file is corrupt or unreadable, initialize with an empty list to avoid crashes
            self.employees = []

    def save_employees(self) -> Tuple[bool, str]:
        """Saves current employee list to the JSON database file."""
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                data = [emp.to_dict() for emp in self.employees]
                json.dump(data, f, indent=4)
            return True, ""
        except OSError as e:
            return False, f"Failed to save data: {e.strerror or str(e)}"

    def get_all_employees(self) -> List[Employee]:
        """Returns all employees in the system."""
        return self.employees

    def search_by_id(self, employee_id: str) -> Optional[Employee]:
        """Searches for an employee by ID (case-insensitive)."""
        if not employee_id:
            return None
        
        cleaned_id = employee_id.strip().lower()
        for emp in self.employees:
            if emp.employee_id.lower() == cleaned_id:
                return emp
        return None

    def add_employee(self, employee: Employee) -> Tuple[bool, str]:
        """Validates and adds a new employee. Prevents duplicate IDs."""
        # Run validations
        valid_id, err_id = Employee.validate_id(employee.employee_id)
        if not valid_id:
            return False, err_id

        valid_name, err_name = Employee.validate_name(employee.name)
        if not valid_name:
            return False, err_name

        valid_email, err_email = Employee.validate_email(employee.email)
        if not valid_email:
            return False, err_email

        valid_date, err_date = Employee.validate_joining_date(employee.joining_date)
        if not valid_date:
            return False, err_date

        # Check duplicate
        if self.search_by_id(employee.employee_id) is not None:
            return False, f"Employee ID '{employee.employee_id}' already exists."

        self.employees.append(employee)
        success, err = self.save_employees()
        if not success:
            return False, err
        return True, "Employee added successfully."

    def update_employee(self, employee_id: str, name: Optional[str] = None, email: Optional[str] = None,
                        department: Optional[str] = None, designation: Optional[str] = None,
                        joining_date: Optional[str] = None) -> Tuple[bool, str]:
        """Updates details of an existing employee. Only updates modified fields, validating them first."""
        emp = self.search_by_id(employee_id)
        if not emp:
            return False, f"Employee with ID '{employee_id}' not found."

        # Validate updates if provided
        if name is not None:
            valid_name, err_name = Employee.validate_name(name)
            if not valid_name:
                return False, err_name
            emp.name = name.strip()

        if email is not None:
            valid_email, err_email = Employee.validate_email(email)
            if not valid_email:
                return False, err_email
            emp.email = email.strip()

        if department is not None:
            emp.department = department.strip()

        if designation is not None:
            emp.designation = designation.strip()

        if joining_date is not None:
            valid_date, err_date = Employee.validate_joining_date(joining_date)
            if not valid_date:
                return False, err_date
            emp.joining_date = joining_date.strip()

        success, err = self.save_employees()
        if not success:
            return False, err
        return True, "Employee updated successfully."

    def delete_employee(self, employee_id: str) -> Tuple[bool, str]:
        """Deletes an employee by ID."""
        emp = self.search_by_id(employee_id)
        if not emp:
            return False, f"Employee with ID '{employee_id}' not found."

        self.employees.remove(emp)
        success, err = self.save_employees()
        if not success:
            return False, err
        return True, "Employee deleted successfully."

    def get_employees_sorted_by_name(self, reverse: bool = False) -> List[Employee]:
        """Returns employees sorted by name (case-insensitive)."""
        return sorted(self.employees, key=lambda x: x.name.lower(), reverse=reverse)

    def filter_employees_by_department(self, department: str) -> List[Employee]:
        """Returns employees belonging to a specific department (case-insensitive exact match)."""
        if not department:
            return []
        cleaned_dept = department.strip().lower()
        return [emp for emp in self.employees if emp.department.lower() == cleaned_dept]
