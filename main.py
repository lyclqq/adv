from flask import Flask,render_template,url_for,redirect,make_response,session,request,flash,send_from_directory,g
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
from config import Config
from app import create_app

app=create_app('develop')


#自定义出错页
@app.errorhandler(404)
def page_not_found(e):
    return '页面没找到'


@app.route('/temp')
def temp():
    return render_template('temp.html',temp='Hello')



if __name__=='__main__':
    app.run('0.0.0.0', port=80, debug=True)