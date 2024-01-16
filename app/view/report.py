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
    c = bar2()
    return Markup(c.render_embed())


@report_bp.route('/report/chart', methods=["GET", "POST"])
def report_chart():
    return render_template('report/chart.html')


def bar2() -> Bar:
    x = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]
    y1 = [931.43, 319.52, 975.69, 725.81, 784.84, 1524.20, 935.60, 1021.20, 1050.02, 1637.42, 1500, 1400]
    y2 = [668.73, 563.61, 1098.05, 884.65, 828.02, 1509.48, 949.97, 1012.22, 1199.45, 1090.48, 900, 1000]
    #
    # x = []
    # y1 = []
    # y2 = []
    # sum11 = func.sum(Orders.Fee11).label('sum11')
    # sum41 = func.sum(Orders.Fee41).label('sum41')
    # fee_sum = Orders.query.with_entities(Orders.group_id, sum11, sum41).group_by(Orders.group_id).all()
    # for f in fee_sum:
    #     gs = Groups.query.filter(Groups.id == f.group_id).first()
    #     x.append(gs.groupname)
    #     y1.append(f.sum11)
    #     y2.append(f.sum41)
    ##
    c = (
        Bar()
        .add_xaxis(x)
        .add_yaxis("2022年刊登金额", y1)
        .add_yaxis("2023年刊登金额", y2)
        .set_global_opts(title_opts=opts.TitleOpts(title="", subtitle=""))
    )
    return c


@report_bp.route("/report/bar")
def get_bar_chart():
    x = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]
    y1 = [931.43, 319.52, 975.69, 725.81, 784.84, 1524.20, 935.60, 1021.20, 1050.02, 1637.42, 1500, 1400]
    c = (
        Bar()
        .add_xaxis(x)
        .add_yaxis("刊登金额", y1)
        .set_global_opts(title_opts=opts.TitleOpts(title="", subtitle=""))
    )
    return c.dump_options_with_quotes()


@report_bp.route("/report/barChart")
def get_bar2_chart():
    c = bar2()
    return c.dump_options_with_quotes()


@report_bp.route("/report/line")
def get_line():
    x_data = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]
    y_data = [668.73, 1232.34, 2330.39, 3215.05, 4043.07, 5552.55, 6502.52, 7514.74, 8714.19, 9804.67, 10000, 10040]
    y2_data = [931.43, 1250.95, 2226.64, 2952.45, 3737.29, 5261.49, 6197.09, 7218.29, 8268.31, 9905.73, 11000, 11050]
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
    # x_data = []
    # y_data = []
    # sum11 = func.sum(Orders.Fee11).label('sum11')
    # fee_sum = Orders.query.with_entities(Orders.group_id, sum11).group_by(Orders.group_id).all()
    # for f in fee_sum:
    #     gs = Groups.query.filter(Groups.id == f.group_id).first()
    #     x_data.append(gs.groupname)
    #     y_data.append(f.sum11)
    #
    x_data = ["新余事业部", "萍乡事业部", "抚州事业部", "工交事业部", "三农事业部", "吉安事业部", "法治事业部", "赣州事业部", "光影事业部",
              "南昌事业部", "九江事业部", "财贸事业部", "社会事业部", "金融事业部", "宜春事业部", "体育公司", "健康事业部", "教育事业部", "鹰潭事业部",
              "上饶事业部", "广告部", "景德镇事业部", "工会事业部", "智库事业部", "会展事业部"]
    y_data = [148.42, 292.12, 459.31, 611.76, 648.78, 282.00, 351.70, 843.36, 230.80, 1136.38, 706.25, 464.13, 259.75, 776.81,
              458.69, 219.50, 557.20, 591.51, 118.70, 292.50, 104.10, 114.50, 89.40, 34.00, 13.00]
    #
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
