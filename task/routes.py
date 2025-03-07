from fastapi import APIRouter, Depends, HTTPException
from models import Student, Test, TestResult, ResponseMessage
from db import students_db, tests_db, test_results_db
from utils import get_student, get_test
from auth import (
    get_current_user,
    get_current_admin,
    get_current_instructor,
    Token,
    authenticate_user,
    create_access_token,
    User,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    timedelta,
    status,
)

students_router = APIRouter(prefix="/students", tags=["Students"])
tests_router = APIRouter(prefix="/tests", tags=["Tests"])
results_router = APIRouter(prefix="/results", tags=["Results"])

@students_router.post("/", response_model=Student)
def create_student(
    student: Student,
    current_user: User = Depends(get_current_admin),  # Only admin can create students
):
    if student.id in students_db:
        raise HTTPException(status_code=400, detail="Student ID already exists")
    students_db[student.id] = student
    return student

@students_router.get("/{student_id}/", response_model=Student)
def get_student_by_id(
    student_id: int,
    current_user: User = Depends(get_current_user),  # Authenticated users only
):
    student = get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@students_router.get("/", response_model=list[Student])
def get_all_students(
    current_user: User = Depends(get_current_user),  # Authenticated users only
):
    return list(students_db.values())

@students_router.delete("/{student_id}/", response_model=ResponseMessage)
def delete_student(
    student_id: int,
    current_user: User = Depends(get_current_admin),  # Only admin can delete students
):
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    del students_db[student_id]
    global test_results_db
    test_results_db = [result for result in test_results_db if result.student_id != student_id]
    return ResponseMessage(message="Student deleted successfully")

@tests_router.post("/", response_model=Test)
def create_test(
    test: Test,
    current_user: User = Depends(get_current_instructor),  # Only instructors can create tests
):
    if test.id in tests_db:
        raise HTTPException(status_code=400, detail="Test ID already exists")
    tests_db[test.id] = test
    return test

@tests_router.get("/{test_id}/", response_model=Test)
def get_test_by_id(
    test_id: int,
    current_user: User = Depends(get_current_user),  # Authenticated users only
):
    test = get_test(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return test

@tests_router.get("/", response_model=list[Test])
def get_all_tests(
    current_user: User = Depends(get_current_user),  # Authenticated users only
):
    return list(tests_db.values())

@results_router.post("/", response_model=ResponseMessage)
def submit_test_result(
    result: TestResult,
    current_user: User = Depends(get_current_instructor),  # Only instructors can submit results
):
    student = get_student(result.student_id)
    test = get_test(result.test_id)
    if not student or not test:
        raise HTTPException(status_code=404, detail="Student or Test not found")
    if result.score > test.max_score:
        raise HTTPException(status_code=400, detail="Score exceeds maximum allowed")
    test_results_db.append(result)
    student.tests_taken.append(result.test_id)
    return ResponseMessage(message="Test result submitted successfully")

@results_router.get("/student/{student_id}/", response_model=list[TestResult])
def get_all_test_results_for_student(
    student_id: int,
    current_user: User = Depends(get_current_user),  # Authenticated users only
):
    student = get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return [result for result in test_results_db if result.student_id == student_id]

@results_router.get("/test/{test_id}/", response_model=list[TestResult])
def get_all_test_results_for_test(
    test_id: int,
    current_user: User = Depends(get_current_user),  # Authenticated users only
):
    test = get_test(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return [result for result in test_results_db if result.test_id == test_id]

@results_router.get("/test/{test_id}/average", response_model=float)
def get_average_score_for_test(
    test_id: int,
    current_user: User = Depends(get_current_user),  # Authenticated users only
):
    test = get_test(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    results = [result.score for result in test_results_db if result.test_id == test_id]
    if not results:
        raise HTTPException(status_code=404, detail="No results found for this test")
    return sum(results) / len(results)

@results_router.get("/test/{test_id}/highest", response_model=int)
def get_highest_score_for_test(
    test_id: int,
    current_user: User = Depends(get_current_user),  # Authenticated users only
):
    test = get_test(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    results = [result.score for result in test_results_db if result.test_id == test_id]
    if not results:
        raise HTTPException(status_code=404, detail="No results found for this test")
    return max(results)