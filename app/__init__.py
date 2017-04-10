from flask import Flask

app = Flask(__name__)

from app import index_old
from app import index
from app import login_register
from app import stock_old
from app import stock
from app import dynamo