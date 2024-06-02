# run_code.py
import sys

def execute_user_code():
    print('Executing user code...')
    try:
        #import sys
        file_name = sys.argv[1]
        print(f'File name: {file_name}')
        with open(file_name, 'r') as code_file:
            code = code_file.read()
        exec_globals = {}
        exec(code, exec_globals)
        result = exec_globals.get('result', 'No result variable defined.')
        print(result)
        return result
    except Exception as e:
        print(e)
        with open('output.txt', 'w') as output_file:
            output_file.write(str(e))

if __name__ == '__main__':
    execute_user_code()