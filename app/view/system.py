# -*- coding: utf-8 -*-

from flask import Blueprint,render_template,current_app,url_for,redirect,session,request,flash,g
import json
import os
from functools import wraps
from app.common import is_login
from app import db
from sqlalchemy import or_, and_, not_

systemView=Blueprint('system',__name__)

