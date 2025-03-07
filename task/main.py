from fastapi import FastAPI
from routes import students_router, tests_router, results_router
from auth import auth_router

app = FastAPI(title="Student Application Testing System")
@app.get("/")
def read_root():
    return {"message": "Welcome to the Student Application Testing System"}


app.include_router(auth_router)
app.include_router(students_router)
app.include_router(tests_router)
app.include_router(results_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)