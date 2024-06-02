# run_code.py

# def execute_user_code():
#     print("Executing user code...")
#     try:
#         # import sys
#         file_name = sys.argv[1]
#         print(f"File name: {file_name}")
#         with open(file_name, "r") as code_file:
#             code = code_file.read()
#         exec_globals = {}
#         exec(code, exec_globals)
#         result = exec_globals.get("result", "No result variable defined.")
#         print(result)
#         return result
#     except Exception as e:
#         print(e)
#         with open("output.txt", "w") as output_file:
#             output_file.write(str(e))


# if __name__ == "__main__":
#     execute_user_code()
import sys
import pandas as pd
import scipy


def run_user_code(code):
    try:
        # Execute the user-provided code
        exec(code, {"pd": pd, "scipy": scipy})
        return "Code executed successfully", None
    except Exception as e:
        return None, str(e)


if __name__ == "__main__":
    code = sys.stdin.read()
    result, error = run_user_code(code)
    if error:
        print(f"Error: {error}")
    else:
        print(result)
