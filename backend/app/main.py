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

    client = docker.from_env()
    image = "python-sandbox"  # Using the base Python image

    # Create the Docker container
    container = client.containers.run(
        image, "sleep infinity", detach=True  # Keep the container running
    )

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
        exit_code = exec_result.exit_code
        print("this is exit code", exit_code)

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

    finally:
        # Clean up the container
        container.remove(force=True)


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

    client = docker.from_env()
    image = "python-sandbox"  # Using the base Python image

    # Create the Docker container

    container = client.containers.run(
        image, "sleep infinity", detach=True  # Keep the container running
    )

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
        exit_code = exec_result.exit_code
        print("this is exit code", exit_code)

    finally:
        # Clean up the container
        container.remove(force=True)

    return {"result": output}


@app.post("/executecode")
async def run_code(request: Request):
    json_data = await request.json()
    print(json_data)
    user_code = json_data["code"]

    # user_code file  name shoudl be unique
    user_code_file = f"user_code_{uuid.uuid4()}.py"

    with open(user_code_file, "w") as code_file:
        code_file.write(user_code)

    client = docker.from_env()
    # Define the host directory to mount
    host_directory = os.getcwd()
    container_directory = "/app"

    image = "python-sandbox"

    # Run the Docker container with the volume mount
    container = client.containers.run(
        image,  # Replace with your image name
        f"python run_code.py {user_code_file}",  # Command or arguments to pass to the container
        volumes={
            host_directory: {
                "bind": container_directory,
                "mode": "rw",
            }
        },
        remove=True,  # Automatically remove the container when it exits
        detach=True,  # Run the container in detached mode
    )
    # Stream the logs from the container
    for line in container.logs(stream=True):
        print(line.strip().decode("utf-8"))

    # Wait for the container to finish
    result = container.wait()
    return result

    code = "print('This is user python code') \nresult = 1 + 2 \nprint(result)"
    with open("user_code.py", "w") as code_file:
        code_file.write(code)

    # Build the Docker image
    build_process = subprocess.run(
        ["docker", "build", "-t", "python-sandbox", "."], capture_output=True
    )
    if build_process.returncode != 0:
        return (
            json.dumps(
                {
                    "status": "error",
                    "message": "Failed to build Docker image",
                    "details": build_process.stderr.decode(),
                }
            ),
            500,
        )

    # Run the Docker container
    run_process = subprocess.run(
        ["docker", "run", "--rm", "-v", f"{os.getcwd()}:/app", "python-sandbox"],
        capture_output=True,
    )
    if run_process.returncode != 0:
        return (
            json.dumps(
                {
                    "status": "error",
                    "message": "Failed to run Docker container",
                    "details": run_process.stderr.decode(),
                }
            ),
            500,
        )

    # Read the output from the output.txt file
    with open("output.txt", "r") as output_file:
        result = output_file.read()

    return json.dumps({"status": "success", "result": result})
