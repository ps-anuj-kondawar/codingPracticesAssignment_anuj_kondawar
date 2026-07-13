import sys
from typing import List, Optional, Callable, Tuple
from models.employee import Employee
from services.employee_service import EmployeeService

# ANSI Escape Codes for CLI styling
COLOR_HEADER = "\033[1;36m"   # Bold Cyan
COLOR_SUCCESS = "\033[1;32m"  # Bold Green
COLOR_ERROR = "\033[1;31m"    # Bold Red
COLOR_WARNING = "\033[1;33m"  # Bold Yellow
COLOR_INFO = "\033[1;34m"     # Bold Blue
COLOR_RESET = "\033[0m"       # Reset formatting

class EmployeeConsoleApp:
    """Console application for interacting with the Employee Management System."""

    def __init__(self) -> None:
        # Defaults database file to employees.json
        self.service = EmployeeService()

    def print_menu(self) -> None:
        """Prints the main interactive menu."""
        print(f"\n{COLOR_HEADER}================================================={COLOR_RESET}")
        print(f"{COLOR_HEADER}         EMPLOYEE MANAGEMENT SYSTEM (EMS)        {COLOR_RESET}")
        print(f"{COLOR_HEADER}================================================={COLOR_RESET}")
        print(" 1. Add New Employee")
        print(" 2. View All Employees (with Sorting & Filtering)")
        print(" 3. Search Employee by ID")
        print(" 4. Update Employee Details")
        print(" 5. Delete Employee")
        print(" 6. Exit Application")
        print(f"{COLOR_HEADER}-------------------------------------------------{COLOR_RESET}")

    def prompt_input(self, prompt_text: str, validator: Optional[Callable[[str], Tuple[bool, str]]] = None, 
                     allow_cancel: bool = True) -> Optional[str]:
        """Prompts for input and validates it. Loop continues until valid input or cancellation."""
        while True:
            try:
                val = input(prompt_text).strip()
                if allow_cancel and val.lower() == 'cancel':
                    print(f"{COLOR_WARNING}Operation cancelled.{COLOR_RESET}")
                    return None
                
                if validator:
                    is_valid, err_msg = validator(val)
                    if not is_valid:
                        print(f"{COLOR_ERROR}Validation Error: {err_msg}{COLOR_RESET}")
                        if allow_cancel:
                            print(f"Type '{COLOR_WARNING}cancel{COLOR_RESET}' to abort this operation.")
                        continue
                return val
            except (KeyboardInterrupt, EOFError):
                print(f"\n{COLOR_WARNING}Input interrupted. Operation cancelled.{COLOR_RESET}")
                return None

    def display_employee_table(self, employees: List[Employee]) -> None:
        """Prints employee records in a beautiful, structured ASCII table."""
        if not employees:
            print(f"{COLOR_WARNING}No employee records found.{COLOR_RESET}")
            return

        # Column headers and default sizes
        col_headers = {
            "id": "Employee ID",
            "name": "Name",
            "email": "Email Address",
            "dept": "Department",
            "desg": "Designation",
            "date": "Joining Date"
        }

        # Dynamically calculate the maximum width for each column to keep tables aligned
        col_widths = {
            "id": max(len(col_headers["id"]), max(len(e.employee_id) for e in employees)),
            "name": max(len(col_headers["name"]), max(len(e.name) for e in employees)),
            "email": max(len(col_headers["email"]), max(len(e.email) for e in employees)),
            "dept": max(len(col_headers["dept"]), max(len(e.department) for e in employees)),
            "desg": max(len(col_headers["desg"]), max(len(e.designation) for e in employees)),
            "date": max(len(col_headers["date"]), max(len(e.joining_date) for e in employees))
        }

        # Build borders and row format strings
        border = (f"+-{'-' * col_widths['id']}-+-{'-' * col_widths['name']}-+-"
                  f"{'-' * col_widths['email']}-+-{'-' * col_widths['dept']}-+-"
                  f"{'-' * col_widths['desg']}-+-{'-' * col_widths['date']}-+")
        
        header_row = (f"| {col_headers['id'].ljust(col_widths['id'])} | "
                      f"{col_headers['name'].ljust(col_widths['name'])} | "
                      f"{col_headers['email'].ljust(col_widths['email'])} | "
                      f"{col_headers['dept'].ljust(col_widths['dept'])} | "
                      f"{col_headers['desg'].ljust(col_widths['desg'])} | "
                      f"{col_headers['date'].ljust(col_widths['date'])} |")

        print(f"\n{COLOR_INFO}{border}{COLOR_RESET}")
        print(f"{COLOR_INFO}{header_row}{COLOR_RESET}")
        print(f"{COLOR_INFO}{border}{COLOR_RESET}")

        for emp in employees:
            row = (f"| {emp.employee_id.ljust(col_widths['id'])} | "
                   f"{emp.name.ljust(col_widths['name'])} | "
                   f"{emp.email.ljust(col_widths['email'])} | "
                   f"{emp.department.ljust(col_widths['dept'])} | "
                   f"{emp.designation.ljust(col_widths['desg'])} | "
                   f"{emp.joining_date.ljust(col_widths['date'])} |")
            print(row)
            
        print(f"{COLOR_INFO}{border}{COLOR_RESET}")

    def add_employee_flow(self) -> None:
        """Guides the user through the process of adding a new employee."""
        print(f"\n{COLOR_HEADER}--- Add New Employee ---{COLOR_RESET}")
        print("Provide details below or type 'cancel' to return.")

        # 1. ID Check (must not exist)
        def validate_unique_id(emp_id: str) -> Tuple[bool, str]:
            valid, err = Employee.validate_id(emp_id)
            if not valid:
                return False, err
            if self.service.search_by_id(emp_id) is not None:
                return False, f"Employee ID '{emp_id}' is already registered."
            return True, ""

        emp_id = self.prompt_input("Employee ID: ", validate_unique_id)
        if emp_id is None: return

        # 2. Name Check
        name = self.prompt_input("Full Name: ", Employee.validate_name)
        if name is None: return

        # 3. Email Check
        email = self.prompt_input("Email: ", Employee.validate_email)
        if email is None: return

        # 4. Department (can be anything but let's enforce not empty)
        def validate_non_empty_dept(dept: str) -> Tuple[bool, str]:
            if not dept.strip():
                return False, "Department name cannot be empty."
            return True, ""
        department = self.prompt_input("Department: ", validate_non_empty_dept)
        if department is None: return

        # 5. Designation (validate not empty)
        def validate_non_empty_desg(desg: str) -> Tuple[bool, str]:
            if not desg.strip():
                return False, "Designation cannot be empty."
            return True, ""
        designation = self.prompt_input("Designation: ", validate_non_empty_desg)
        if designation is None: return

        # 6. Joining Date Check
        joining_date = self.prompt_input("Joining Date (YYYY-MM-DD): ", Employee.validate_joining_date)
        if joining_date is None: return

        # Construct and Add
        new_emp = Employee(emp_id, name, email, department, designation, joining_date)
        success, msg = self.service.add_employee(new_emp)
        if success:
            print(f"\n{COLOR_SUCCESS}Success: {msg}{COLOR_RESET}")
        else:
            print(f"\n{COLOR_ERROR}Error: {msg}{COLOR_RESET}")

    def view_employees_flow(self) -> None:
        """Displays menu for listing, sorting, and filtering employees."""
        while True:
            print(f"\n{COLOR_HEADER}--- View Employee Records ---{COLOR_RESET}")
            print(" 1. View All Employees (Default)")
            print(" 2. View Sorted by Name (A-Z)")
            print(" 3. View Sorted by Name (Z-A)")
            print(" 4. Filter by Department")
            print(" 5. Return to Main Menu")
            print(f"{COLOR_HEADER}-----------------------------{COLOR_RESET}")
            
            choice = input("Select an option (1-5): ").strip()
            
            if choice == '1':
                self.display_employee_table(self.service.get_all_employees())
            elif choice == '2':
                self.display_employee_table(self.service.get_employees_sorted_by_name(reverse=False))
            elif choice == '3':
                self.display_employee_table(self.service.get_employees_sorted_by_name(reverse=True))
            elif choice == '4':
                dept = input("Enter department name to filter: ").strip()
                if not dept:
                    print(f"{COLOR_WARNING}Filtering skipped. Empty department name provided.{COLOR_RESET}")
                    continue
                filtered = self.service.filter_employees_by_department(dept)
                self.display_employee_table(filtered)
            elif choice == '5':
                break
            else:
                print(f"{COLOR_ERROR}Invalid selection. Please choose 1 to 5.{COLOR_RESET}")

    def search_employee_flow(self) -> None:
        """Prompts for an ID and prints the corresponding record in table format."""
        print(f"\n{COLOR_HEADER}--- Search Employee ---{COLOR_RESET}")
        emp_id = input("Enter Employee ID to search: ").strip()
        if not emp_id:
            print(f"{COLOR_ERROR}Employee ID cannot be empty.{COLOR_RESET}")
            return

        emp = self.service.search_by_id(emp_id)
        if emp:
            self.display_employee_table([emp])
        else:
            print(f"{COLOR_ERROR}Employee with ID '{emp_id}' not found.{COLOR_RESET}")

    def update_employee_flow(self) -> None:
        """Guides user to update specific fields of an employee."""
        print(f"\n{COLOR_HEADER}--- Update Employee Details ---{COLOR_RESET}")
        emp_id = input("Enter Employee ID to update: ").strip()
        if not emp_id:
            print(f"{COLOR_ERROR}Employee ID cannot be empty.{COLOR_RESET}")
            return

        emp = self.service.search_by_id(emp_id)
        if not emp:
            print(f"{COLOR_ERROR}Employee with ID '{emp_id}' not found.{COLOR_RESET}")
            return

        print(f"\nEmployee found. Press Enter to keep current values, or type 'cancel' to abort.")

        # Prompt for Name
        name_input = self.prompt_input(f"Name [{emp.name}]: ", lambda x: (True, "") if not x else Employee.validate_name(x))
        if name_input is None: return
        name = name_input if name_input else None

        # Prompt for Email
        email_input = self.prompt_input(f"Email [{emp.email}]: ", lambda x: (True, "") if not x else Employee.validate_email(x))
        if email_input is None: return
        email = email_input if email_input else None

        # Prompt for Department
        dept_input = self.prompt_input(f"Department [{emp.department}]: ", None)
        if dept_input is None: return
        dept = dept_input if dept_input else None

        # Prompt for Designation
        desg_input = self.prompt_input(f"Designation [{emp.designation}]: ", None)
        if desg_input is None: return
        desg = desg_input if desg_input else None

        # Prompt for Joining Date
        date_input = self.prompt_input(f"Joining Date [{emp.joining_date}] (YYYY-MM-DD): ", 
                                        lambda x: (True, "") if not x else Employee.validate_joining_date(x))
        if date_input is None: return
        date = date_input if date_input else None

        # Perform the updates
        success, msg = self.service.update_employee(
            employee_id=emp.employee_id,
            name=name,
            email=email,
            department=dept,
            designation=desg,
            joining_date=date
        )

        if success:
            print(f"\n{COLOR_SUCCESS}Success: {msg}{COLOR_RESET}")
        else:
            print(f"\n{COLOR_ERROR}Error: {msg}{COLOR_RESET}")

    def delete_employee_flow(self) -> None:
        """Deletes an employee from system after user confirmation."""
        print(f"\n{COLOR_HEADER}--- Delete Employee ---{COLOR_RESET}")
        emp_id = input("Enter Employee ID to delete: ").strip()
        if not emp_id:
            print(f"{COLOR_ERROR}Employee ID cannot be empty.{COLOR_RESET}")
            return

        emp = self.service.search_by_id(emp_id)
        if not emp:
            print(f"{COLOR_ERROR}Employee with ID '{emp_id}' not found.{COLOR_RESET}")
            return

        confirm = input(f"{COLOR_WARNING}Are you sure you want to delete {emp.name} (ID: {emp.employee_id})? (y/N): {COLOR_RESET}").strip().lower()
        if confirm == 'y' or confirm == 'yes':
            success, msg = self.service.delete_employee(emp_id)
            if success:
                print(f"\n{COLOR_SUCCESS}Success: {msg}{COLOR_RESET}")
            else:
                print(f"\n{COLOR_ERROR}Error: {msg}{COLOR_RESET}")
        else:
            print(f"{COLOR_INFO}Deletion aborted.{COLOR_RESET}")

    def start(self) -> None:
        """Starts the main application loop."""
        while True:
            self.print_menu()
            choice = input("Enter your option (1-6): ").strip()
            
            if choice == '1':
                self.add_employee_flow()
            elif choice == '2':
                self.view_employees_flow()
            elif choice == '3':
                self.search_employee_flow()
            elif choice == '4':
                self.update_employee_flow()
            elif choice == '5':
                self.delete_employee_flow()
            elif choice == '6':
                print(f"\n{COLOR_SUCCESS}Thank you for using the Employee Management System! Goodbye.{COLOR_RESET}\n")
                sys.exit(0)
            else:
                print(f"{COLOR_ERROR}Invalid selection. Please choose an option from 1 to 6.{COLOR_RESET}")

if __name__ == "__main__":
    app = EmployeeConsoleApp()
    app.start()
