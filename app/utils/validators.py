import re

def validate_student_name(name):
    """
    Validate student name.
    
    Args:
        name: Student name string
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "Name cannot be empty"
    
    if len(name.strip()) < 2:
        return False, "Name is too short"
    
    return True, ""

def validate_student_id(student_id):
    """
    Validate student ID.
    
    Args:
        student_id: Student ID string
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not student_id or not student_id.strip():
        return False, "Student ID cannot be empty"
    
    # Remove spaces for validation
    student_id = student_id.strip().replace(" ", "")
    
    if len(student_id) < 5:
        return False, "Student ID is too short"
    
    return True, ""

def validate_module_name(module_name):
    """
    Validate module name.
    
    Args:
        module_name: Module name string
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not module_name or not module_name.strip():
        return False, "Module name cannot be empty"
    
    if len(module_name.strip()) < 3:
        return False, "Module name is too short"
    
    return True, ""

def validate_module_code(module_code):
    """
    Validate module code with relaxed rules to support various formats.
    
    Args:
        module_code: Module code string
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not module_code or not module_code.strip():
        return False, "Module code cannot be empty"
    
    code = module_code.strip()
    
    # Minimum length check
    if len(code) < 4:
        return False, "Module code is too short (minimum 4 characters)"
    
    # Maximum length check
    if len(code) > 10:
        return False, "Module code is too long (maximum 10 characters)"
    
    # More flexible pattern - allows various formats
    # Examples: SE2052, CSC1234, CS-2052, COMP101, IT-3133, MAT101
    if not re.match(r'^[A-Z]{2,4}[-]?\d{3,4}$', code, re.IGNORECASE):
        return False, "Module code format should be like: SE2052, CSC1234, or CS-2052"
    
    return True, ""

def validate_practical_number(practical_num):
    """
    Validate practical number.
    
    Args:
        practical_num: Practical number (int or string)
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        num = int(practical_num)
        if num < 1 or num > 99:
            return False, "Sheet number should be between 1 and 99"
        return True, ""
    except (ValueError, TypeError):
        return False, "Sheet number must be a valid number"