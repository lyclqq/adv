import os
import xlwt
from flask import Blueprint, render_template, current_app, make_response, session, send_from_directory
from jinja2 import Markup, Environment, FileSystemLoader
from nanoid import generate
##from pyecharts.faker import Faker
from pyecharts.globals import CurrentConfig
from pyecharts import options as opts
from pyecharts.charts import Bar, Pie, Line
from sqlalchemy import func, create_engine
# from sqlalchemy.sql.elements import and_
# from datetime import datetime
# from app.models.bill import Fee2
from app import db
from app.models.contract import Orders
from app.models.other import Reports
from app.models.system import Groups

# 关于 CurrentConfig，可参考 [基本使用-全局变量]
CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("app/templates/pyecharts"))

report_bp = Blueprint('report', __name__)


@report_bp.route('/report/test', methods=["GET", "POST"])
def report_test():
    c = bar_base()
    return Markup(c.render_embed())


@report_bp.route('/report/chart', methods=["GET", "POST"])
def report_chart():
    return render_template('report/chart.html')


def bar_base() -> Bar:
    # x = ["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子", "hehe"]
    # y1 = [5, 20, 36, 10, 75, 90, 44]
    # y2 = [15, 25, 16, 55, 48, 8, 60]
    x = []
    y1 = []
    y2 = []
    sum11 = func.sum(Orders.Fee11).label('sum11')
    sum41 = func.sum(Orders.Fee41).label('sum41')
    fee_sum = Orders.query.with_entities(Orders.group_id, sum11, sum41).group_by(Orders.group_id).all()
    for f in fee_sum:
        gs = Groups.query.filter(Groups.id == f.group_id).first()
        x.append(gs.groupname)
        y1.append(f.sum11)
        y2.append(f.sum41)
    c = (
        Bar()
        .add_xaxis(x)
        .add_yaxis("合同金额", y1)
        .add_yaxis("到账金额", y2)
        .set_global_opts(title_opts=opts.TitleOpts(title="", subtitle=""))
    )
    return c


@report_bp.route("/report/barChart")
def get_bar_chart():
    c = bar_base()
    return c.dump_options_with_quotes()


@report_bp.route("/report/line")
def get_line():
    x_data = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    y_data = [820, 932, 901, 934, 1290, 1330, 1320]
    y2_data = [720, 632, 401, 1034, 990, 1530, 1320]
    ##
    # x_data = []
    # y_data = []
    # sum11 = func.sum(Orders.Fee11).label('sum11')
    # fee_sum = Orders.query.with_entities(Orders.group_id, sum11).group_by(Orders.group_id).all()
    # for f in fee_sum:
    #     gs = Groups.query.filter(Groups.id == f.group_id).first()
    #     x_data.append(gs.groupname)
    #     y_data.append(f.sum11)

    # from app.models.other import History
    # History.query.all()

    line = (
        Line()
        .set_global_opts(
            tooltip_opts=opts.TooltipOpts(is_show=False),
            xaxis_opts=opts.AxisOpts(type_="category"),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        )
        .add_xaxis(xaxis_data=x_data)
        .add_yaxis(
            series_name="总合同金额",
            y_axis=y_data,
            symbol="emptyCircle",
            is_symbol_show=True,
            label_opts=opts.LabelOpts(is_show=True)
        ).add_yaxis(
            series_name="总合同金额",
            y_axis=y2_data,
            symbol="emptyCircle",
            is_symbol_show=True,
            label_opts=opts.LabelOpts(is_show=True)
        ))
    return line.dump_options_with_quotes()


@report_bp.route("/report/pie")
def get_pie():
    x_data = []
    y_data = []
    sum11 = func.sum(Orders.Fee11).label('sum11')
    fee_sum = Orders.query.with_entities(Orders.group_id, sum11).group_by(Orders.group_id).all()
    for f in fee_sum:
        gs = Groups.query.filter(Groups.id == f.group_id).first()
        x_data.append(gs.groupname)
        y_data.append(f.sum11)
    c = (
        Pie()
        .add("总合同金额", [list(z) for z in zip(
            x_data,
            y_data
        )])
        .set_global_opts(title_opts=opts.TitleOpts(title=""))
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    )
    return c.dump_options_with_quotes()


@report_bp.route("/report/list")
def report_perf():
    # t_format = '%Y-%m-%d'
    # date_b = '2023-12-01'
    # date_e = '2023-12-11'
    result = get_report_data()
    return render_template('report/list.html', result=result)


def get_report_data():
    engine = create_engine(current_app.config['SQLALCHEMY_DATABASE_URI'], echo=False)
    with engine.connect() as conn:
        result_proxy = conn.execute("select a.*,fee4.fee,fee4.feedate,fee3.id from "
                                    "(select order_id,"
                                    "group_concat(concat_ws(',',feedate) order by feedate asc) as 'dates',"
                                    "type,sum(fee) as 'fees',0 as 'bid',round(sum(fee)/1.06,2) as 'fee106',"
                                    "0.16 as 'ratio',round(sum(fee)/1.06*0.16,0) as 'perf' "
                                    "from fee2 group by order_id,type order by order_id,type) "
                                    "a,fee4,fee3 "
                                    "where  a.order_id=fee4.order_id and fee4.order_id=fee3.order_id")
        result = result_proxy.fetchall()
    return result


report_file_path = os.path.join('static', 'files', 'report')


def set_cell_style(bold=False, center=True):
    #
    font = xlwt.Font()
    font.name = '仿宋_GB2312'
    font.height = HEIGHT_BASE * 16
    if bold:
        font.bold = True
    #
    pattern_top = xlwt.Pattern()
    pattern_top.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern_top.pattern_fore_colour = 5
    #
    align = xlwt.Alignment()
    if center:
        align.horz = xlwt.Alignment.HORZ_CENTER
    align.vert = xlwt.Alignment.VERT_CENTER
    #
    style = xlwt.XFStyle()
    style.font = font
    # style.pattern = pattern_top
    style.alignment = align
    #
    return style


def as_report(filename):
    rp = Reports()
    rp.title = '绩效'
    rp.iuser_id = session.get('user_id')
    rp.filename = filename
    rp.path = report_file_path + os.sep
    rp.type = 'aa'
    return rp


HEIGHT_BASE = 20
WIDTH_BASE = 256


def list_to_excel(data):
    # Reports.query.all()
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("sheet1", cell_overwrite_ok=True)
    sheet.write_merge(1, 1, 0, 13, '4月绩效', set_cell_style(True))
    sheet.row(1).height_mismatch = True
    sheet.row(1).height = HEIGHT_BASE * 30
    #
    sheet.write(2, 0, '序号', set_cell_style())
    sheet.write(2, 1, '刊登（播）单位', set_cell_style())
    sheet.write(2, 2, '刊登日期', set_cell_style())
    sheet.write(2, 3, '刊登类别', set_cell_style())
    sheet.write(2, 4, '业务收入', set_cell_style())
    sheet.write(2, 5, '招投标代理', set_cell_style())
    sheet.write(2, 6, '税后业务收入', set_cell_style())
    sheet.write(2, 7, '到款收入', set_cell_style())
    sheet.write(2, 8, '到款日期', set_cell_style())
    sheet.write(2, 9, '业务绩效比例', set_cell_style())
    sheet.write(2, 10, '实发业务绩效金额', set_cell_style())
    sheet.write(2, 11, '发票编号', set_cell_style())
    sheet.write(2, 12, '经营人员', set_cell_style())
    sheet.write(2, 13, '备注', set_cell_style())
    sheet.row(2).height_mismatch = True
    sheet.row(2).height = HEIGHT_BASE * 30
    #
    fees_sum = 0
    fee106_sum = 0
    perf_sum = 0
    fee_sum = 0
    i = 1
    for re in data:
        sheet.write(2 + i, 0, i, set_cell_style())
        sheet.write(2 + i, 1, re.order_id, set_cell_style())
        sheet.write(2 + i, 2, re.dates, set_cell_style())
        sheet.write(2 + i, 3, re.type, set_cell_style())
        sheet.write(2 + i, 4, re.fees, set_cell_style())
        sheet.write(2 + i, 5, re.bid, set_cell_style())
        sheet.write(2 + i, 6, re.fee106, set_cell_style())
        sheet.write(2 + i, 7, re.fee, set_cell_style())
        sheet.write(2 + i, 8, re.feedate, set_cell_style())
        sheet.write(2 + i, 9, re.ratio, set_cell_style())
        sheet.write(2 + i, 10, re.perf, set_cell_style())
        sheet.write(2 + i, 11, re.id, set_cell_style())
        sheet.write(2 + i, 12, '', set_cell_style())
        sheet.write(2 + i, 13, '', set_cell_style())
        sheet.row(2 + i).height_mismatch = True
        sheet.row(2 + i).height = HEIGHT_BASE * 20
        i += 1
        #
        fees_sum = fees_sum + re.fees
        fee106_sum = fee106_sum + re.fee106
        perf_sum = perf_sum + re.perf
        fee_sum = fee_sum + re.fee
    #
    sheet.write(i + 3, 0, '合计', set_cell_style())
    sheet.write(i + 3, 4, fees_sum, set_cell_style())
    sheet.write(i + 3, 5, 0, set_cell_style())
    sheet.write(i + 3, 6, fee106_sum, set_cell_style())
    sheet.write(i + 3, 7, fee_sum, set_cell_style())
    sheet.write(i + 3, 10, perf_sum, set_cell_style())
    sheet.row(i + 3).height_mismatch = True
    sheet.row(i + 3).height = HEIGHT_BASE * 20
    #
    sheet.write(i + 4, 0, '制表人：', set_cell_style(False, False))
    sheet.write(i + 4, 2, '广告部复核人：', set_cell_style(False, False))
    sheet.write(i + 4, 5, '广告部分管绩效负责人:', set_cell_style(False, False))
    sheet.write(i + 4, 9, '广告部负责人:', set_cell_style(False, False))
    sheet.row(i + 4).height_mismatch = True
    sheet.row(i + 4).height = HEIGHT_BASE * 20
    #
    sheet.write(i + 6, 0, '事业部负责人：', set_cell_style(False, False))
    sheet.write(i + 6, 5, '计划财务部稽核人：', set_cell_style(False, False))
    sheet.write(i + 6, 9, '计划财务部负责人：', set_cell_style(False, False))
    sheet.row(i + 6).height_mismatch = True
    sheet.row(i + 6).height = HEIGHT_BASE * 20
    #
    sheet.write(i + 8, 0, '经管办复核人：', set_cell_style(False, False))
    sheet.write(i + 8, 2, '经管办稽核人：', set_cell_style(False, False))
    sheet.write(i + 8, 5, '经管办分管负责人：', set_cell_style(False, False))
    sheet.write(i + 8, 9, '经管办负责人：', set_cell_style(False, False))
    sheet.row(i + 8).height_mismatch = True
    sheet.row(i + 8).height = HEIGHT_BASE * 20
    #
    filename = generate(size=10) + '.xls'
    # 列宽
    for i in range(1, 13):
        sheet.col(i).width = WIDTH_BASE * 20
    #
    workbook.save(current_app.root_path + os.sep + report_file_path + os.sep + filename)
    rp = as_report(filename)
    db.session.add(rp)
    db.session.commit()


@report_bp.route("/report/gen")
def report_gen():
    data = get_report_data()
    list_to_excel(data)
    return '成功'


@report_bp.route("/report/down", methods=['GET'])
def report_down():
    rp = Reports.query.order_by(Reports.create_datetime.desc()).first()
    print(rp.id)
    name = rp.filename
    dd = current_app.root_path + os.sep + report_file_path + os.sep
    is_file = os.path.isfile(dd + name)
    if is_file:
        response = make_response(send_from_directory(dd, name, download_name=name, as_attachment=True))
        return response
    else:
        return '文件不存在'
