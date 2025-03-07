from pydantic import BaseModel, Field
from typing import List, Optional

class Student(BaseModel):
    id: int = Field(..., description="Unique identifier for the student")
    name: str = Field(..., min_length=2, max_length=50, description="Student's full name")
    email: str = Field(..., description="Student's email address")
    tests_taken: List[int] = []

class Test(BaseModel):
    id: int = Field(..., description="Unique identifier for the test")
    name: str = Field(..., min_length=2, max_length=100, description="Name of the test")
    max_score: int = Field(..., description="Maximum possible score")

class TestResult(BaseModel):
    student_id: int = Field(..., description="ID of the student taking the test")
    test_id: int = Field(..., description="ID of the test taken")
    score: int = Field(..., description="Score obtained in the test")

class ResponseMessage(BaseModel):
    message: str