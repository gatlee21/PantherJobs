# Author: Graham Atlee
# Main entry into running the flask app

from pantherjobs import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)