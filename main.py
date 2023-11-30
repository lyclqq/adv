import datetime
import os
from flask import render_template, url_for, session, request, send_from_directory
from flask_ckeditor import upload_fail, upload_success
from app import create_app, db
from app.common import is_login

app=create_app('develop')


#自定义出错页
@app.errorhandler(404)
def page_not_found(e):
    return '页面没找到'


@app.route('/temp')
def temp():
    db.drop_all()
    db.create_all()
    return render_template('temp.html',temp='Hello')


@app.route('/files/<int:dirname>/<filename>')
@app.route('/Files/<int:dirname>/<filename>')
def up_file(dirname,filename):
    #print(str(dirname)+'filename='+filename)
    return send_from_directory(app.config['UPLOADED_PATH'],str(dirname)+'/'+filename)


@app.route('/Files/<filename>')
@app.route('/files/<filename>')
def uploaded_files(filename):
    path=os.path.join(app.config['UPLOADED_PATH'],datetime.datetime.now().strftime("%Y")+os.sep)
    return send_from_directory(app.config['UPLOADED_PATH'], filename)


#附件上传
@app.route('/upload', methods=['POST'],endpoint='upload')
@is_login
def upload():
    f = request.files.get('upload')
    extension = f.filename.split('.')[-1].lower()
    if extension not in ['jpg', 'gif', 'png', 'jpeg','doc','xls','docx','xlsx']:
        return upload_fail(message='只能上传图片、word和excel文件!')
    newfilename=session.get('username')+datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    path=os.path.join(app.config['UPLOADED_PATH'],datetime.datetime.now().strftime("%Y")+os.sep)
    if not os.path.exists(path):
        os.mkdir(path)
    #print(os.path.join(path, newfilename+'.'+extension))
    f.save(os.path.join(path, newfilename+'.'+extension))
    url = url_for('uploaded_files', filename=datetime.datetime.now().strftime("%Y")+'/'+newfilename+'.'+extension)
    return upload_success(url=url)


if __name__=='__main__':
    app.run('0.0.0.0', port=80, debug=True)