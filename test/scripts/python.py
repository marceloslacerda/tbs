import sys

output_message = 'test successful'
error_message = 'test error'
help_message = 'test help'

if __name__ == '__main__':
    if sys.argv[1] == '--help':
        print(help_message)
    elif sys.argv[1] == '-e':
        sys.stderr.write(error_message + '\n')
    else:
        print(output_message)