from flask import Flask, render_template, request
import random
from gcprand import GcpDot

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def random_string():
    string_length = 128  # default length
    error_message = None  # Initialize error message variable

    if request.method == 'POST':
        try:
            # Attempt to convert input to an integer
            string_length = int(request.form.get('length', 128))

            # Check if the length is within the allowed range
            if string_length < 1 or string_length > 1000:
                error_message = "Length must be between 1 and 1000."
                string_length = 128  # Reset to default if out of range

        except ValueError:
            # Set an error message if the input is not a valid integer
            error_message = "Please enter a valid integer for the string length."
            string_length = 128  # Reset to default if input is invalid

    # Create an instance of the GcpDot class
    g = GcpDot("D:\\geckodriver.exe")

    # Set the seed for the random number generator
    seed = g.random()
    print("Seed: " + str(seed))

    random.seed(seed)

    # Generate a random string of specified length
    random_string = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=string_length))
    return render_template('index.html', random_string=random_string, error_message=error_message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
