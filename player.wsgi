#!I:\Python27\python.exe
import os
import sys

root = os.path.dirname(os.path.abspath(__file__))
 
activate_this = os.path.join(root, 'flask/Scripts/activate_this.py')
execfile(activate_this, dict(__file__=activate_this))
 
sys.path.insert(0, root)

from app import app as application

if __name__ == '__main__':
    application.run()
