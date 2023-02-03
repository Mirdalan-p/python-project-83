from flask import Flask, render_template, request, redirect


app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello world!'