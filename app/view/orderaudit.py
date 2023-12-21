# -*- coding: utf-8 -*-

from flask import Blueprint,render_template,current_app,url_for,redirect,session,request,flash,g
import json
import os
from functools import wraps
from app.common import is_login,ins_logs
from app import db
from app.models.contract import Customers,Orders
from app.models.other import Files
from app.forms.customer import CustomerForm
from app.forms.order import OrderForm,OrderSearchForm,OrderupfileForm
import datetime

orderauditView=Blueprint('order_audit',__name__)