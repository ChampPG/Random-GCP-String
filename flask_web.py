from flask import Flask, render_template, request
import random
from gcprand import GcpDot

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def random_string():
    string_length = 128  # default length
    if request.method == 'POST':
        string_length = int(request.form.get('length', 128))

    # Create an instance of the GcpDot class
    g = GcpDot("D:\\geckodriver.exe")

    # Set the seed for the random number generator
    seed = g.random()
    print("Seed: " + str(seed))

    random.seed(seed)

    # Generate a random string of 10 characters
    random_string = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=string_length))
    return render_template('index.html', random_string=random_string)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
