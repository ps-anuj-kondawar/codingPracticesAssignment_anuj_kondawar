from typing import List, Optional, Tuple, Union
from models.employee import Employee
from models.exceptions import DatabaseError
from repositories.employee_repository import EmployeeRepository, JSONEmployeeRepository


class EmployeeService:
    """Handles business logic for employee management, including validation, search, sorting, filtering, and persistence coordination."""

    def __init__(self, repository_or_path: Optional[Union[EmployeeRepository, str]] = None) -> None:
        """Initializes EmployeeService with a repository or database file path."""
        if isinstance(repository_or_path, EmployeeRepository):
            self.repository: EmployeeRepository = repository_or_path
        elif isinstance(repository_or_path, str):
            self.repository = JSONEmployeeRepository(repository_or_path)
        else:
            self.repository = JSONEmployeeRepository("employees.json")

        self.employees: List[Employee] = []
        self.load_employees()

    def load_employees(self) -> None:
        """Loads employees from the repository into memory.

        Raises:
            CorruptDataError: If the persistence file is corrupt or unreadable.
            StorageError: If reading the file fails due to an I/O error.
        """
        self.employees = self.repository.load_all()

    def get_all_employees(self) -> List[Employee]:
        """Returns a copy of all employees in the system."""
        return list(self.employees)

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
        """Validates and adds a new employee. Prevents duplicate IDs.

        Guarantees state consistency: if saving fails, in-memory state is rolled back.
        """
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

        if self.search_by_id(employee.employee_id) is not None:
            return False, f"Employee ID '{employee.employee_id}' already exists."

        # Stage in-memory change
        self.employees.append(employee)

        # Attempt persistence with rollback on failure
        try:
            self.repository.save_all(self.employees)
        except DatabaseError as exc:
            self.employees.pop()  # Rollback
            return False, f"Failed to save data: {str(exc)}"

        return True, "Employee added successfully."

    def update_employee(
        self,
        employee_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        department: Optional[str] = None,
        designation: Optional[str] = None,
        joining_date: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Updates details of an existing employee.

        Validates all inputs before applying changes and rolls back in-memory state if persistence fails.
        """
        emp = self.search_by_id(employee_id)
        if not emp:
            return False, f"Employee with ID '{employee_id}' not found."

        # Pre-validate all changes before modifying any attributes
        if name is not None:
            valid_name, err_name = Employee.validate_name(name)
            if not valid_name:
                return False, err_name

        if email is not None:
            valid_email, err_email = Employee.validate_email(email)
            if not valid_email:
                return False, err_email

        if joining_date is not None:
            valid_date, err_date = Employee.validate_joining_date(joining_date)
            if not valid_date:
                return False, err_date

        # Snapshot old values for atomic rollback
        old_name = emp.name
        old_email = emp.email
        old_department = emp.department
        old_designation = emp.designation
        old_joining_date = emp.joining_date

        # Apply updates
        if name is not None:
            emp.name = name.strip()
        if email is not None:
            emp.email = email.strip()
        if department is not None:
            emp.department = department.strip()
        if designation is not None:
            emp.designation = designation.strip()
        if joining_date is not None:
            emp.joining_date = joining_date.strip()

        # Attempt persistence with rollback on failure
        try:
            self.repository.save_all(self.employees)
        except DatabaseError as exc:
            # Rollback to exact snapshot
            emp.name = old_name
            emp.email = old_email
            emp.department = old_department
            emp.designation = old_designation
            emp.joining_date = old_joining_date
            return False, f"Failed to save data: {str(exc)}"

        return True, "Employee updated successfully."

    def delete_employee(self, employee_id: str) -> Tuple[bool, str]:
        """Deletes an employee by ID.

        Guarantees state consistency: if saving fails, in-memory state is rolled back.
        """
        emp = self.search_by_id(employee_id)
        if not emp:
            return False, f"Employee with ID '{employee_id}' not found."

        index = self.employees.index(emp)
        removed_emp = self.employees.pop(index)

        # Attempt persistence with rollback on failure
        try:
            self.repository.save_all(self.employees)
        except DatabaseError as exc:
            self.employees.insert(index, removed_emp)  # Rollback
            return False, f"Failed to save data: {str(exc)}"

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
