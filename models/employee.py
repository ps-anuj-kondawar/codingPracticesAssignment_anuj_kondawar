import re
from datetime import datetime
from typing import Tuple, Dict, Any

class Employee:
    """Represents an Employee with basic details and validation methods."""

    def __init__(self, employee_id: str, name: str, email: str, department: str, designation: str, joining_date: str):
        self.employee_id = employee_id.strip()
        self.name = name.strip()
        self.email = email.strip()
        self.department = department.strip()
        self.designation = designation.strip()
        self.joining_date = joining_date.strip()

    @staticmethod
    def validate_id(employee_id: str) -> Tuple[bool, str]:
        """Validates that the Employee ID is not empty."""
        cleaned_id = employee_id.strip() if employee_id else ""
        if not cleaned_id:
            return False, "Employee ID cannot be empty."
        return True, ""

    @staticmethod
    def validate_name(name: str) -> Tuple[bool, str]:
        """Validates that the Name is not empty."""
        cleaned_name = name.strip() if name else ""
        if not cleaned_name:
            return False, "Name cannot be empty."
        return True, ""

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validates that the email matches a standard format and is not empty."""
        cleaned_email = email.strip() if email else ""
        if not cleaned_email:
            return False, "Email cannot be empty."
        
        # Standard email validation regex
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_regex, cleaned_email):
            return False, "Email is invalid. Please use a format like user@domain.com."
        return True, ""

    @staticmethod
    def validate_joining_date(joining_date: str) -> Tuple[bool, str]:
        """Validates that the joining date is in YYYY-MM-DD format."""
        cleaned_date = joining_date.strip() if joining_date else ""
        if not cleaned_date:
            return False, "Joining date cannot be empty."
        
        try:
            datetime.strptime(cleaned_date, "%Y-%m-%d")
            return True, ""
        except ValueError:
            return False, "Joining date must be in YYYY-MM-DD format."

    def to_dict(self) -> Dict[str, str]:
        """Serializes the employee object to a dictionary."""
        return {
            "employee_id": self.employee_id,
            "name": self.name,
            "email": self.email,
            "department": self.department,
            "designation": self.designation,
            "joining_date": self.joining_date
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Employee':
        """Deserializes a dictionary into an Employee object."""
        return cls(
            employee_id=data.get("employee_id", ""),
            name=data.get("name", ""),
            email=data.get("email", ""),
            department=data.get("department", ""),
            designation=data.get("designation", ""),
            joining_date=data.get("joining_date", "")
        )
