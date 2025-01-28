import re
from django.core.management.base import BaseCommand
from accounts.models import User
from jobsapp.models import EmployeeProfile, ImportError, DecimalEncoder
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from django.db import transaction
import json

class Command(BaseCommand):
    help = 'Import employees from SQL file'

    def add_arguments(self, parser):
        parser.add_argument('sql_file', type=str, help='Path to the SQL file')
        parser.add_argument('--create-users', action='store_true', help='Create user accounts for employees')

    def parse_date(self, value):
        if not value or value.lower() == 'null':
            return None
        
        # Try different date formats
        formats = [
            '%d/%m/%Y',           # 31/12/2023
            '%Y-%m-%d %H:%M:%S',  # 2023-12-31 00:00:00
            '%Y-%m-%d'            # 2023-12-31
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(value.strip(), fmt).date()
            except ValueError:
                continue
        
        return None

    def parse_year(self, value):
        if not value or value.lower() == 'null':
            return None
        
        try:
            # Try to extract year from date string first
            for fmt in ['%Y-%m-%d %H:%M:%S', '%d/%m/%Y', '%Y-%m-%d']:
                try:
                    return datetime.strptime(value.strip(), fmt).year
                except ValueError:
                    continue
                
            # If not a date string, try direct integer conversion
            return int(value.strip())
        except (ValueError, TypeError):
            return None

    def parse_salary(self, value):
        """Parse salary values safely"""
        if not value or value.lower() == 'null':
            return None
        try:
            # Remove any currency symbols, commas and spaces
            clean_value = str(value).replace(',', '').replace('ETB', '').strip()
            if clean_value:
                return Decimal(clean_value)
            return None
        except (ValueError, InvalidOperation, TypeError):
            return None

    def clean_value(self, val):
        if not val or val.lower() == 'null':
            return None
        # Remove N prefix and quotes
        if val.startswith('N\''):
            val = val[2:-1]  # Remove N' from start and ' from end
        elif val.startswith('N"'):
            val = val[2:-1]  # Remove N" from start and " from end
        elif val.startswith("'"):
            val = val[1:-1]  # Remove quotes
        elif val.startswith('"'):
            val = val[1:-1]  # Remove quotes
        
        # Remove any leading 'N' if it still exists
        if val.startswith('N'):
            val = val[1:]
        
        return val.strip()

    def handle_import_error(self, row_number, employee_name, file_no, error_type, error_message, raw_values):
        """Handle import errors by logging them"""
        try:
            # Convert raw values to a format that can be JSON serialized
            processed_values = []
            if isinstance(raw_values, (list, tuple)):
                for value in raw_values:
                    if isinstance(value, Decimal):
                        processed_values.append(str(value))
                    elif isinstance(value, (datetime, date)):
                        processed_values.append(value.isoformat())
                    elif value is None:
                        processed_values.append(None)
                    else:
                        processed_values.append(str(value))
            else:
                # If raw_values is not iterable, convert it to string
                processed_values = str(raw_values)

            # Create the error log
            ImportError.objects.create(
                row_number=row_number,
                employee_name=str(employee_name) if employee_name else 'Unknown',
                file_no=str(file_no) if file_no else 'Unknown',
                error_type=str(error_type),
                error_message=str(error_message),
                raw_values=processed_values
            )
            
            # Return True if error was logged successfully
            return True
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Failed to log error for row {row_number}: {str(e)}\n'
                    f'Original error: {error_type} - {error_message}'
                )
            )
            return False

    def process_row(self, values, total_records):
        """Process a single row of employee data"""
        try:
            # Map values to fields
            employee_data = {
                'file_no': self.clean_value(values[1]),  # FILE_No
                'id_no': self.clean_value(values[2]),    # ID_No
                'pid_no': self.clean_value(values[3]),   # PID_No
                'tin_no': self.clean_value(values[4]),   # TIN_No
                'name_of_employee': self.clean_value(values[5]),  # Name_of_Employee
                'name_of_employee_in_amharic': self.clean_value(values[6]),  # Name_of_Employee_in_Amharic
                'sex': self.clean_value(values[7]),      # Sex
                'date_of_birth': self.parse_date(values[8]),  # Date_of_Birth
                'date_of_employment': self.parse_date(values[10]) or datetime(2000, 1, 1).date(),  # Date_of_Employment
                'job_category': self.clean_value(values[12]),  # Job_Category
                'previous_position': self.clean_value(values[13]),  # Previous_Postion
                'new_position': self.clean_value(values[14]),  # New_Position
                'old_jg': self.clean_value(values[15]),  # Old_JG
                'new_jg': self.clean_value(values[16]),  # New_JG
                'working_unit': self.clean_value(values[17]),  # Working_Unit
                'district': self.clean_value(values[18]),  # District
                'place_of_assignment': self.clean_value(values[19]),  # Place_of_Assignment
                'region': self.clean_value(values[20]),  # Region
            }

            # Handle salary fields separately with proper Decimal conversion
            salary_fields = {
                'july_promoted_salary': values[21],
                'new_salary': values[22],
                'old_salary_2022_23_inc': values[23],
                'old_salary_2021_22_inc': values[24],
                'old_salary_2020_2021': values[25],
                'old_salary_2019_2020': values[26],
                'old_salary_2018_2019': values[27],
                'old_salary_2017_18': values[28],
                'old_salary_2016_17': values[29]
            }

            for field, value in salary_fields.items():
                try:
                    parsed_value = self.parse_salary(value)
                    employee_data[field] = parsed_value
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Warning: Could not parse salary for field {field} in row {total_records}. Value: {value}"
                        )
                    )
                    employee_data[field] = None

            # Add remaining fields
            employee_data.update({
                'educational_level': self.clean_value(values[30]),
                'field_of_study': self.clean_value(values[31]),
                'university_college': self.clean_value(values[32]),
                'year_of_graduation': self.parse_year(values[33]),
                'cost_sharing_status': self.clean_value(values[34]),
                'processed_by': self.clean_value(values[35]),
                'branch_grading': self.clean_value(values[36]),
                'is_active': True
            })

            return employee_data

        except Exception as e:
            raise Exception(f"Error processing row data: {str(e)}")

    def handle(self, *args, **options):
        sql_file = options['sql_file']
        create_users = options['create_users']
        
        try:
            with open(sql_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract all value groups using regex
            pattern = r'\((.*?)\)(?:\s*,\s*(?=\()|\s*$)'
            matches = re.findall(pattern, content)
            
            total_records = 0
            success_count = 0
            error_count = 0
            updated_count = 0
            
            for match in matches:
                total_records += 1
                try:
                    # Split the values and clean them
                    values = []
                    current_value = ''
                    in_quotes = False
                    for char in match + ',':
                        if char == "'" and (len(current_value) == 0 or current_value[-1] != '\\'):
                            in_quotes = not in_quotes
                        elif char == ',' and not in_quotes:
                            # Clean the value
                            val = self.clean_value(current_value.strip())
                            values.append(val)
                            current_value = ''
                        else:
                            current_value += char
                    
                    # Process the row
                    employee_data = self.process_row(values, total_records)
                    
                    # Auto-generate file number if missing
                    if not employee_data['file_no']:
                        base_id = employee_data['id_no'] or employee_data['tin_no'] or values[0]
                        employee_data['file_no'] = f"TEMP-{base_id}"
                        employee_data['processed_by'] = f"AUTO-GENERATED File No ({employee_data['processed_by'] or 'Import Script'})"
                        self.stdout.write(f"Auto-generated file number {employee_data['file_no']} for {employee_data['name_of_employee']}")
                    
                    if create_users:
                        try:
                            # Try to get existing user
                            email = f"{employee_data['name_of_employee'].lower().replace(' ', '.')}@berhan-bank.com"
                            user, created = User.objects.get_or_create(
                                email=email,
                                defaults={
                                    'password': "Welcome@2024",
                                    'first_name': employee_data['name_of_employee'].split()[0],
                                    'last_name': ' '.join(employee_data['name_of_employee'].split()[1:]),
                                    'role': 'employee',
                                    'gender': employee_data['sex'].lower()
                                }
                            )
                            if created:
                                self.stdout.write(f"Created new user account for {email}")
                            else:
                                self.stdout.write(f"Found existing user account for {email}")
                            employee_data['user'] = user
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f"Could not create/get user for {employee_data['name_of_employee']}: {str(e)}"))
                    
                    # Create or update employee record
                    with transaction.atomic():
                        employee, created = EmployeeProfile.objects.update_or_create(
                            file_no=employee_data['file_no'],
                            defaults=employee_data
                        )
                        
                        if created:
                            self.stdout.write(f"Created employee record for {employee_data['name_of_employee']}")
                            success_count += 1
                        else:
                            self.stdout.write(f"Updated employee record for {employee_data['name_of_employee']}")
                            updated_count += 1
                    
                except Exception as e:
                    error_count += 1
                    error_logged = self.handle_import_error(
                        total_records, 
                        employee_data.get('name_of_employee'), 
                        employee_data.get('file_no'), 
                        type(e).__name__, 
                        str(e), 
                        values
                    )
                    
                    # Only print error details if logging failed
                    if not error_logged:
                        self.stdout.write(f"\nERROR DETAILS for row {total_records}:")
                        self.stdout.write(f"Employee Name: {employee_data.get('name_of_employee', 'Unknown')}")
                        self.stdout.write(f"File No: {employee_data.get('file_no', 'Unknown')}")
                        self.stdout.write(f"Error Type: {type(e).__name__}")
                        self.stdout.write(f"Error Message: {str(e)}")
            
            self.stdout.write("\nImport completed:")
            self.stdout.write(f"Total records processed: {total_records}")
            self.stdout.write(f"Successfully imported: {success_count}")
            self.stdout.write(f"Successfully updated: {updated_count}")
            self.stdout.write(f"Errors: {error_count}")
            
        except Exception as e:
            self.stdout.write(f"Error reading SQL file: {str(e)}") 