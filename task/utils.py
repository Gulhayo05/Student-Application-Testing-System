from db import students_db, tests_db

def get_student(student_id: int):
    return students_db.get(student_id)

def get_test(test_id: int):
    return tests_db.get(test_id)