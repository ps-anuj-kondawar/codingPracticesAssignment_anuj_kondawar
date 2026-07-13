import unittest
import os
import sys

# Ensure project root is in the path so we can import models and services
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.employee import Employee
from services.employee_service import EmployeeService

class TestEmployeeService(unittest.TestCase):
    """Unit tests for EmployeeService business logic."""

    def setUp(self) -> None:
        """Sets up a clean test database file before each test."""
        self.db_path = "test_employees.json"
        # Make sure no leftover file exists
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.service = EmployeeService(self.db_path)

    def tearDown(self) -> None:
        """Cleans up the test database file after each test."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_add_valid_employee(self) -> None:
        emp = Employee("EMP001", "John Doe", "john.doe@example.com", "Engineering", "Software Engineer", "2026-07-13")
        success, msg = self.service.add_employee(emp)
        self.assertTrue(success)
        self.assertEqual(len(self.service.get_all_employees()), 1)
        self.assertEqual(self.service.get_all_employees()[0].name, "John Doe")

    def test_add_duplicate_employee_id(self) -> None:
        emp1 = Employee("EMP001", "John Doe", "john.doe@example.com", "Engineering", "Software Engineer", "2026-07-13")
        self.service.add_employee(emp1)
        emp2 = Employee("EMP001", "Jane Doe", "jane.doe@example.com", "HR", "Recruiter", "2026-07-13")
        success, msg = self.service.add_employee(emp2)
        self.assertFalse(success)
        self.assertIn("already exists", msg)

    def test_add_invalid_email(self) -> None:
        emp = Employee("EMP001", "John Doe", "john.doe-invalid", "Engineering", "Software Engineer", "2026-07-13")
        success, msg = self.service.add_employee(emp)
        self.assertFalse(success)
        self.assertIn("Email is invalid", msg)

    def test_add_invalid_date(self) -> None:
        emp = Employee("EMP001", "John Doe", "john.doe@example.com", "Engineering", "Software Engineer", "13-07-2026")
        success, msg = self.service.add_employee(emp)
        self.assertFalse(success)
        self.assertIn("YYYY-MM-DD", msg)

    def test_search_by_id(self) -> None:
        emp = Employee("EMP001", "John Doe", "john.doe@example.com", "Engineering", "Software Engineer", "2026-07-13")
        self.service.add_employee(emp)
        found = self.service.search_by_id("EMP001")
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "John Doe")
        # Test case-insensitivity of search
        found_lower = self.service.search_by_id("emp001")
        self.assertIsNotNone(found_lower)

    def test_update_employee(self) -> None:
        emp = Employee("EMP001", "John Doe", "john.doe@example.com", "Engineering", "Software Engineer", "2026-07-13")
        self.service.add_employee(emp)
        
        success, msg = self.service.update_employee("EMP001", name="Johnathan Doe", department="R&D")
        self.assertTrue(success)
        updated_emp = self.service.search_by_id("EMP001")
        self.assertIsNotNone(updated_emp)
        self.assertEqual(updated_emp.name, "Johnathan Doe")
        self.assertEqual(updated_emp.department, "R&D")
        self.assertEqual(updated_emp.email, "john.doe@example.com") # Unchanged

    def test_delete_employee(self) -> None:
        emp = Employee("EMP001", "John Doe", "john.doe@example.com", "Engineering", "Software Engineer", "2026-07-13")
        self.service.add_employee(emp)
        success, msg = self.service.delete_employee("EMP001")
        self.assertTrue(success)
        self.assertIsNone(self.service.search_by_id("EMP001"))

    def test_sorting_by_name(self) -> None:
        emp1 = Employee("EMP001", "Zachary Smith", "zach@example.com", "HR", "Recruiter", "2026-07-13")
        emp2 = Employee("EMP002", "Alice Johnson", "alice@example.com", "Engineering", "Developer", "2026-07-13")
        emp3 = Employee("EMP003", "Bob Miller", "bob@example.com", "Engineering", "Manager", "2026-07-13")
        
        self.service.add_employee(emp1)
        self.service.add_employee(emp2)
        self.service.add_employee(emp3)
        
        sorted_list = self.service.get_employees_sorted_by_name()
        self.assertEqual(sorted_list[0].name, "Alice Johnson")
        self.assertEqual(sorted_list[1].name, "Bob Miller")
        self.assertEqual(sorted_list[2].name, "Zachary Smith")

    def test_filtering_by_department(self) -> None:
        emp1 = Employee("EMP001", "Alice Johnson", "alice@example.com", "Engineering", "Developer", "2026-07-13")
        emp2 = Employee("EMP002", "Bob Miller", "bob@example.com", "Engineering", "Manager", "2026-07-13")
        emp3 = Employee("EMP003", "Zachary Smith", "zach@example.com", "HR", "Recruiter", "2026-07-13")
        
        self.service.add_employee(emp1)
        self.service.add_employee(emp2)
        self.service.add_employee(emp3)
        
        filtered = self.service.filter_employees_by_department("Engineering")
        self.assertEqual(len(filtered), 2)
        
        filtered_hr = self.service.filter_employees_by_department("hr")
        self.assertEqual(len(filtered_hr), 1)
        self.assertEqual(filtered_hr[0].name, "Zachary Smith")

if __name__ == '__main__':
    unittest.main()
