import base64
from multiprocessing import Manager, Process, Queue, process
from fastapi import FastAPI, HTTPException, Request
import os
import subprocess
import json
import docker
import uuid
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_URL = "postgresql://ryanhu@localhost/codeeditor"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class CodeExecution(Base):
    __tablename__ = "code_execution"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(Text, nullable=False)
    output = Column(Text, nullable=False)


Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://localhost:5173",  # Frontend URL for development
    # Add other origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def run_code_in_container(encoded_code, result):
    client = docker.from_env()
    image = "python-sandbox"  # Using the base Python image
    print("this is encoded code", encoded_code)

    # Create the Docker container
    container = client.containers.run(
        image,
        "sleep infinity",
        detach=True,
        security_opt=["no-new-privileges"],  # Drop unnecessary privileges
        cap_drop=["ALL"],
        working_dir="/app",  # Set the working directory to /app',
        # Drop all capabilities
        # Keep the container running
    )
    print(f"Created container {container.id}")
    for container in client.containers.list():
        print(container.id, container.status)

    try:
        # Copy the user code to the container using base64 decoding
        container.exec_run(
            f"sh -c 'echo {encoded_code} | base64 -d > /app/run_code.py'"
        )

        # Run the user code inside the container
        exec_result = container.exec_run(
            "python /app/run_code.py", stdout=True, stderr=True
        )

        # Get the output and error streams
        output = exec_result.output.decode("utf-8")
        print("this is output", output)
        exit_code = exec_result.exit_code

        result.put((output, exit_code))
        print("this is result", result)

    finally:
        # Clean up the container
        container.remove(force=True)
        print(f"Removed container {container.id}")

    print("Containers after removal:")
    for container in client.containers.list():
        print(container.id, container.status)


@app.post("/executeandstorecode")
async def execute_and_store_code(request: Request):
    json_data = await request.json()
    print(json_data)
    user_code = json_data["code"]
    #     user_code = """
    # print('This is user python code123')
    # result = 1 + 2
    # print(result)
    # """

    # Encode the user code to base64
    encoded_code = base64.b64encode(user_code.encode("utf-8")).decode("utf-8")

    output_queue = Queue()
    process = Process(target=run_code_in_container, args=(encoded_code, output_queue))
    process.start()
    process.join(timeout=10)  # Set a timeout of 10 seconds

    if process.is_alive():
        process.terminate()
        process.join()
        return {"result": "Timeout: Code execution took too long"}

    if not output_queue.empty():
        output, exit_code = output_queue.get()
    else:
        output, exit_code = "Error during code execution", 1

    if exit_code == 0:
        # Save the code and output to the database if no error
        db = SessionLocal()
        code_execution = CodeExecution(code=user_code, output=output)
        db.add(code_execution)
        db.commit()
        db.refresh(code_execution)
        db.close()
        return {"result": output, "id": code_execution.id}
    else:
        return {"result": "Error running code", "output": output}


@app.get("/checkcode/{code_id}")
async def check_code(code_id: int):
    db = SessionLocal()
    code_execution = db.query(CodeExecution).filter(CodeExecution.id == code_id).first()
    db.close()
    if code_execution is None:
        raise HTTPException(status_code=404, detail="Code execution not found")
    return {
        "id": code_execution.id,
        "code": code_execution.code,
        "output": code_execution.output,
    }


@app.post("/executecodetest")
async def run_code(request: Request):
    # Hardcoded user code
    json_data = await request.json()
    print(json_data)
    user_code = json_data["code"]

    encoded_code = base64.b64encode(user_code.encode("utf-8")).decode("utf-8")

    output_queue = Queue()
    process = Process(target=run_code_in_container, args=(encoded_code, output_queue))
    process.start()
    process.join(timeout=10)  # Set a timeout of 10 seconds

    if process.is_alive():
        process.terminate()
        process.join()
        return {"result": "Timeout: Code execution took too long"}

    if not output_queue.empty():
        output, exit_code = output_queue.get()
    else:
        output, exit_code = "Error during code execution", 1

    return {"result": output}
