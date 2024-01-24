# -*- coding: utf-8 -*-
from wtforms import StringField, PasswordField, SubmitField, widgets, DateField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length


# 登陆
class LoginForm(FlaskForm):
    # username = StringField( validators=[DataRequired(), Length(1, 20)])
    username = StringField(label='用户名:',
                           validators=[
                               DataRequired(message='用户名不能为空'),
                               Length(min=1, max=25, message='用户名长度必须大于%(min)d且小于%(max)d')
                           ],
                           widget=widgets.TextInput(),
                           render_kw={'class': 'form-control',
                                      "placeholder": "输入注册用户名"}
                           )
    password = PasswordField(
        label='用户密码：',
        validators=[
            DataRequired(message='密码不能为空'),
        ],
        widget=widgets.PasswordInput(),
        render_kw={'class': 'form-control',
                   "placeholder": "输入用户密码"}
    )
    verify_code = StringField('验证码', validators=[DataRequired(), Length(1, 4)],
                              render_kw={'class': 'form-control', "placeholder": "输入验证码"})
    submit = SubmitField('登录', render_kw={'class': 'btn btn-block btn-info'})


class PwdForm(FlaskForm):
    username = StringField(label='用户名:',
                           widget=widgets.TextInput(),
                           render_kw={'class': 'form-control', 'readonly': True}
                           )
    password1 = PasswordField(
        label='输入新用户密码：',
        validators=[
            DataRequired(message='密码不能为空'),
        ],
        widget=widgets.PasswordInput(),
        render_kw={'class': 'form-control',
                   "placeholder": "输入用户密码"}
    )
    password2 = PasswordField(
        label='确认新用户密码：',
        validators=[
            DataRequired(message='密码不能为空'),
        ],
        widget=widgets.PasswordInput(),
        render_kw={'class': 'form-control',
                   "placeholder": "输入用户密码"}
    )
    submit = SubmitField('提交', render_kw={'class': 'btn btn-block btn-info'})


class MonthForm(FlaskForm):
    today = StringField(label='当前月份:',
                        render_kw={'class': 'form-control', 'readonly': 'true'}
                        )
    fee_date = DateField('下一月份', format='%Y-%m', validators=[DataRequired('不能为空')],
                         render_kw={'class': 'form-control', 'height': '60px', 'type': 'month'})
    submit = SubmitField('提交', render_kw={'class': 'btn btn-block btn-info'})
