# -*- coding: utf-8 -*-

import openpyxl
import math
from openpyxl.styles import PatternFill, Border, Side, Alignment, Protection, Font, Color, colors, Style
import base64
import cStringIO
from openerp import models, fields, api, tools
from datetime import datetime, date as d
from calendar import monthrange

MONTHS = [(1, 'January'),
          (2, 'February'),
          (3, 'March'),
          (4, 'April'),
          (5, 'May'),
          (6, 'June'),
          (7, 'July'),
          (8, 'August'),
          (9, 'September'),
          (10, 'October'),
          (11, 'November'),
          (12, 'December')]

YEARS = [(2016, '2016'),
         (2017, '2017'),
         (2018, '2018'),
         (2019, '2019'),
         (2020, '2020')]


def format_date(date):
    return datetime.strptime(date, tools.DEFAULT_SERVER_DATE_FORMAT).strftime('%d.%m.%Y')

def format_float_time(time):
    x = math.modf(time)
    decimal = int(x[0] * 60)
    whole = int(x[1])
    res = str(whole) if whole >= 10 else '0'+str(whole)
    res += ':'
    res += str(decimal) if decimal >= 10 else '0'+str(decimal)
    return res

class EmployeeTimesheetGeneratorLine(models.TransientModel):
    _name = 'employee.timesheet.generator.line'

    employee_timesheet_generator_id = fields.Many2one('employee.timesheet.generator', 'Timesheet generator')
    employee_id = fields.Many2one('hr.employee', 'Employee')
    job_id = fields.Many2one('hr.job', 'Job')

    @api.one
    @api.onchange('employee_id')
    def onchange_employee(self):
        if self.employee_id and self.employee_id.job_id:
            self.job_id = self.employee_id.job_id


class EmployeeTimesheetGenerator(models.TransientModel):
    _name = 'employee.timesheet.generator'

    def _reopen(self, res_id):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Generate XLS timesheets',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': res_id,
            'nodestroy': True,
            'view_id': self.env.ref('project_timesheet_activities.employee_timesheet_generator_form'),
            'res_model': 'employee.timesheet.generator',
            'target': 'new',
        }

    @api.one
    @api.depends('employee_timesheet_generator_line_ids.employee_id')
    def _get_lines_count(self):
        if self.employee_timesheet_generator_line_ids:
            self.lines_count = len(self.employee_timesheet_generator_line_ids)

    data = fields.Binary('File', readonly=True)
    name = fields.Char('File Name', readonly=True)
    month = fields.Selection(MONTHS, 'Month')
    year = fields.Selection(YEARS, 'Year')
    department_id = fields.Many2one('hr.department', 'Department')
    employee_timesheet_generator_line_ids = fields.One2many('employee.timesheet.generator.line',
                                                            'employee_timesheet_generator_id',
                                                            string='Employees')
    state = fields.Selection([('choose', 'Choose'), ('get', 'Get')], 'State', default='choose')
    lines_count = fields.Integer(compute=_get_lines_count, string='Employees count')

    @api.multi
    def fill_lines(self):
        emp_table = self.env['hr.employee']
        emp_gen_lines = self.env['employee.timesheet.generator.line']
        emp_objs = emp_table.search([('department_id', '=', self.department_id.id), ('active', '=', True)])
        for emp in emp_objs:
            local_dict = {
                'employee_timesheet_generator_id': self.id,
                'employee_id': emp.id,
                'job_id': emp.job_id.id,
            }
            emp_gen_lines.create(local_dict)
        return {
            'type': 'ir.actions.act_window',
            'res_id': self[0].id,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'employee.timesheet.generator',
            'target': 'new',
            'context': self.env.context,
        }

    @api.multi
    def get_report(self):
        this = self[0]
        month = this.month
        year = this.year

        start_date = str(year)+'-'+str(month)+'-'+str(monthrange(year, month)[0])
        end_date = str(year)+'-'+str(month)+'-'+str(monthrange(year, month)[1])

        sheet_lines = self.env['account.analytic.line']
        wb = openpyxl.Workbook(encoding='utf-8')

        font_bold = Font(bold=True)
        left = Border(left=Side(color=colors.BLACK, border_style='thick'))
        right = Border(right=Side(color=colors.BLACK, border_style='thick'))
        top = Border(top=Side(color=colors.BLACK, border_style='thick'))
        bottom = Border(bottom=Side(color=colors.BLACK, border_style='thick'))

        for employee in this.employee_timesheet_generator_line_ids:
            analytic_acc_lines = sheet_lines.search([('user_id', '=', employee.employee_id.user_id.id),
                                                     ('is_timesheet', '=', True),
                                                     ('date', '>=', start_date),
                                                     ('date', '<=', end_date)], order='date ASC')
            if not analytic_acc_lines:
                continue

            ws = wb.create_sheet(employee.employee_id.name, 0)


            ws.merge_cells('A2:C2')
            ws['A2'] = 'TIMESHEET'
            ws['C2'].style = Style(border=Border(right=Side(style='thick',
                                                            color=colors.BLACK)))
            ws['A2'].style = Style(font_bold,
                                   border=Border(left=Side(style='thick', color=colors.BLACK),
                                                 right=Side(style='thick', color=colors.BLACK),
                                                 top=Side(style='thick', color=colors.BLACK),
                                                 bottom=Side(style='thick', color=colors.BLACK)),
                                   alignment=Alignment(horizontal='center')
                                   )


            ws.merge_cells('B3:C3')
            ws['A3'] = 'Employee:'
            ws['B3'] = employee.employee_id.name
            ws['C3'].style = Style(border=Border(right=Side(style='thick',
                                                            color=colors.BLACK)))
            ws['B3'].style = Style(
                                   border=Border(left=Side(style='thick', color=colors.BLACK),
                                                 right=Side(style='thick', color=colors.BLACK),
                                                 top=Side(style='thick', color=colors.BLACK),
                                                 bottom=Side(style='thick', color=colors.BLACK)),
                                   alignment=Alignment(horizontal='center')
                                   )

            ws.merge_cells('B4:C4')
            ws['A4'] = 'ID number:'
            ws['B4'] = employee.employee_id.other_id
            ws['C4'].style = Style(border=Border(right=Side(style='thick',
                                                            color=colors.BLACK)))
            ws['B4'].style = Style(
                                   border=Border(left=Side(style='thick', color=colors.BLACK),
                                                 right=Side(style='thick', color=colors.BLACK),
                                                 top=Side(style='thick', color=colors.BLACK),
                                                 bottom=Side(style='thick', color=colors.BLACK)),
                                   alignment=Alignment(horizontal='center')
                                   )

            ws.merge_cells('B5:C5')
            ws['A5'] = 'Month/Year:'
            ws['B5'] = dict(MONTHS).get(month)+' '+dict(YEARS).get(year)
            ws['B5'].font = font_bold
            ws['C5'].style = Style(border=Border(right=Side(style='thick',
                                                            color=colors.BLACK)))
            ws['B5'].style = Style(font_bold,
                                   border=Border(left=Side(style='thick', color=colors.BLACK),
                                                 right=Side(style='thick', color=colors.BLACK),
                                                 top=Side(style='thick', color=colors.BLACK),
                                                 bottom=Side(style='thick', color=colors.BLACK)),
                                   alignment=Alignment(horizontal='center')
                                   )


            ws['A3'].style = Style(
                                   border=Border(left=Side(style='thick', color=colors.BLACK),
                                                 right=Side(style='thick', color=colors.BLACK),
                                                 top=Side(style='thick', color=colors.BLACK),
                                                 bottom=Side(style='thick', color=colors.BLACK)),
                                   )
            ws['A4'].style = Style(
                                   border=Border(left=Side(style='thick', color=colors.BLACK),
                                                 right=Side(style='thick', color=colors.BLACK),
                                                 top=Side(style='thick', color=colors.BLACK),
                                                 bottom=Side(style='thick', color=colors.BLACK)),
                                   )
            ws['A5'].style = Style(
                                   border=Border(left=Side(style='thick', color=colors.BLACK),
                                                 right=Side(style='thick', color=colors.BLACK),
                                                 top=Side(style='thick', color=colors.BLACK),
                                                 bottom=Side(style='thick', color=colors.BLACK)),
                                   )

            ws.merge_cells('E3:H3')
            ws['E3'] = 'Entitlement of holiday days on 31.12.:'
            ws['I3'] = ''
            ws['E3'].style = Style(
                                   border=Border(left=Side(style='thick', color=colors.BLACK),
                                                 right=Side(style='thick', color=colors.BLACK),
                                                 top=Side(style='thick', color=colors.BLACK),
                                                 bottom=Side(style='thick', color=colors.BLACK)),
                                   )
            ws['I3'].style = Style(
                                   border=Border(left=Side(style='thick', color=colors.BLACK),
                                                 right=Side(style='thick', color=colors.BLACK),
                                                 top=Side(style='thick', color=colors.BLACK),
                                                 bottom=Side(style='thick', color=colors.BLACK)),
                                   alignment=Alignment(horizontal='center')
                                   )


            ws.merge_cells('E4:H4')
            ws['E4'] = 'Consumed holiday days:'
            ws['I4'] = ''
            ws['E4'].style = Style(
                                   border=Border(left=Side(style='thick', color=colors.BLACK),
                                                 right=Side(style='thick', color=colors.BLACK),
                                                 top=Side(style='thick', color=colors.BLACK),
                                                 bottom=Side(style='thick', color=colors.BLACK)),
                                   )
            ws['I4'].style = Style(
                                   border=Border(left=Side(style='thick', color=colors.BLACK),
                                                 right=Side(style='thick', color=colors.BLACK),
                                                 top=Side(style='thick', color=colors.BLACK),
                                                 bottom=Side(style='thick', color=colors.BLACK)),
                                   alignment=Alignment(horizontal='center')
                                   )


            ws.merge_cells('E5:H5')
            ws['E5'] = 'Rest of holiday days:'
            ws['I5'] = ''
            ws['E5'].style = Style(
                                   border=Border(left=Side(style='thick', color=colors.BLACK),
                                                 right=Side(style='thick', color=colors.BLACK),
                                                 top=Side(style='thick', color=colors.BLACK),
                                                 bottom=Side(style='thick', color=colors.BLACK)),
                                   )
            ws['I5'].style = Style(
                                   border=Border(left=Side(style='thick', color=colors.BLACK),
                                                 right=Side(style='thick', color=colors.BLACK),
                                                 top=Side(style='thick', color=colors.BLACK),
                                                 bottom=Side(style='thick', color=colors.BLACK)),
                                   alignment=Alignment(horizontal='center')
                                   )

            header_font = Font(bold=True)

            ws['A7'] = 'Date'
            ws['A7'].style = Style(border=Border(left=Side(style='thick', color=colors.BLACK),
                                                 right=Side(style='thick', color=colors.BLACK),
                                                 top=Side(style='thick', color=colors.BLACK),
                                                 bottom=Side(style='thick', color=colors.BLACK)),
                                   alignment=Alignment(wrap_text=True),
                                   font=Font(bold=True),
                                   fill=PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af')))

            ws['B7'] = 'Start'
            ws['B7'].style = Style(border=Border(left=Side(style='thick', color=colors.BLACK),
                                                 right=Side(style='thick', color=colors.BLACK),
                                                 top=Side(style='thick', color=colors.BLACK),
                                                 bottom=Side(style='thick', color=colors.BLACK)),
                                   alignment=Alignment(wrap_text=True),
                                   font=Font(bold=True),
                                   fill=PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af')))

            ws['C7'] = 'End'
            ws['C7'].style = Style(border=Border(left=Side(style='thick', color=colors.BLACK),
                                                 right=Side(style='thick', color=colors.BLACK),
                                                 top=Side(style='thick', color=colors.BLACK),
                                                 bottom=Side(style='thick', color=colors.BLACK)),
                                   alignment=Alignment(wrap_text=True),
                                   font=Font(bold=True),
                                   fill=PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af')))

            ws['D7'] = 'Break'
            ws['D7'].fill = PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af'))
            ws['D7'].font = header_font
            ws['D7'].style = Style(border=Border(left=Side(style='thick', color=colors.BLACK),
                                                 right=Side(style='thick', color=colors.BLACK),
                                                 top=Side(style='thick', color=colors.BLACK),
                                                 bottom=Side(style='thick', color=colors.BLACK)),
                                   alignment=Alignment(wrap_text=True),
                                   font=Font(bold=True),
                                   fill=PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af')))

            ws['E7'] = 'Sum'
            ws['E7'].fill = PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af'))
            ws['E7'].font = header_font
            ws['E7'].style = Style(border=Border(left=Side(style='thick', color=colors.BLACK),
                                                 right=Side(style='thick', color=colors.BLACK),
                                                 top=Side(style='thick', color=colors.BLACK),
                                                 bottom=Side(style='thick', color=colors.BLACK)),
                                   alignment=Alignment(wrap_text=True),
                                   font=Font(bold=True),
                                   fill=PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af')))

            ws['F7'] = 'Working time per day'
            ws['F7'].fill = PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af'))
            ws['F7'].font = header_font
            ws['F7'].style = Style(border=Border(left=Side(style='thick', color=colors.BLACK),
                                                 right=Side(style='thick', color=colors.BLACK),
                                                 top=Side(style='thick', color=colors.BLACK),
                                                 bottom=Side(style='thick', color=colors.BLACK)),
                                   alignment=Alignment(wrap_text=True),
                                   font=Font(bold=True),
                                   fill=PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af')))

            ws['G7'] = 'Project'
            ws['G7'].fill = PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af'))
            ws['G7'].font = header_font
            ws['G7'].style = Style(border=Border(left=Side(style='thick', color=colors.BLACK),
                                                 right=Side(style='thick', color=colors.BLACK),
                                                 top=Side(style='thick', color=colors.BLACK),
                                                 bottom=Side(style='thick', color=colors.BLACK)),
                                   alignment=Alignment(wrap_text=True),
                                   font=Font(bold=True),
                                   fill=PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af')))

            ws['H7'] = 'Activity'
            ws['H7'].fill = PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af'))
            ws['H7'].font = header_font
            ws['H7'].style = Style(border=Border(left=Side(style='thick', color=colors.BLACK),
                                                 right=Side(style='thick', color=colors.BLACK),
                                                 top=Side(style='thick', color=colors.BLACK),
                                                 bottom=Side(style='thick', color=colors.BLACK)),
                                   alignment=Alignment(wrap_text=True),
                                   font=Font(bold=True),
                                   fill=PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af')))

            ws['I7'] = 'Site number'
            ws['I7'].fill = PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af'))
            ws['I7'].font = header_font
            ws['I7'].style = Style(border=Border(left=Side(style='thick', color=colors.BLACK),
                                                 right=Side(style='thick', color=colors.BLACK),
                                                 top=Side(style='thick', color=colors.BLACK),
                                                 bottom=Side(style='thick', color=colors.BLACK)),
                                   alignment=Alignment(wrap_text=True),
                                   font=Font(bold=True),
                                   fill=PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af')))

            ws['J7'] = 'Start travel'
            ws['J7'].fill = PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af'))
            ws['J7'].font = header_font
            ws['J7'].style = Style(border=Border(left=Side(style='thick', color=colors.BLACK),
                                                 right=Side(style='thick', color=colors.BLACK),
                                                 top=Side(style='thick', color=colors.BLACK),
                                                 bottom=Side(style='thick', color=colors.BLACK)),
                                   alignment=Alignment(wrap_text=True),
                                   font=Font(bold=True),
                                   fill=PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af')))

            ws['K7'] = 'End travel'
            ws['K7'].fill = PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af'))
            ws['K7'].font = header_font
            ws['K7'].style = Style(border=Border(left=Side(style='thick', color=colors.BLACK),
                                                 right=Side(style='thick', color=colors.BLACK),
                                                 top=Side(style='thick', color=colors.BLACK),
                                                 bottom=Side(style='thick', color=colors.BLACK)),
                                   alignment=Alignment(wrap_text=True),
                                   font=Font(bold=True),
                                   fill=PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af')))

            ws['L7'] = 'Driver'
            ws['L7'].fill = PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af'))
            ws['L7'].font = header_font
            ws['L7'].style = Style(border=Border(left=Side(style='thick', color=colors.BLACK),
                                                 right=Side(style='thick', color=colors.BLACK),
                                                 top=Side(style='thick', color=colors.BLACK),
                                                 bottom=Side(style='thick', color=colors.BLACK)),
                                   alignment=Alignment(wrap_text=True),
                                   font=Font(bold=True),
                                   fill=PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af')))

            ws['M7'] = 'Vehicle'
            ws['M7'].fill = PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af'))
            ws['M7'].font = header_font
            ws['M7'].style = Style(border=Border(left=Side(style='thick', color=colors.BLACK),
                                                 right=Side(style='thick', color=colors.BLACK),
                                                 top=Side(style='thick', color=colors.BLACK),
                                                 bottom=Side(style='thick', color=colors.BLACK)),
                                   alignment=Alignment(wrap_text=True),
                                   font=Font(bold=True),
                                   fill=PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af')))

            ws['N7'] = 'Accommodation'
            ws['N7'].fill = PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af'))
            ws['N7'].font = header_font
            ws['N7'].style = Style(border=Border(left=Side(style='thick', color=colors.BLACK),
                                                 right=Side(style='thick', color=colors.BLACK),
                                                 top=Side(style='thick', color=colors.BLACK),
                                                 bottom=Side(style='thick', color=colors.BLACK)),
                                   alignment=Alignment(wrap_text=True),
                                   font=Font(bold=True),
                                   fill=PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af')))

            ws['O7'] = 'Travel expense small'
            ws['O7'].fill = PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af'))
            ws['O7'].font = header_font
            ws['O7'].style = Style(border=Border(left=Side(style='thick', color=colors.BLACK),
                                                 right=Side(style='thick', color=colors.BLACK),
                                                 top=Side(style='thick', color=colors.BLACK),
                                                 bottom=Side(style='thick', color=colors.BLACK)),
                                   alignment=Alignment(wrap_text=True),
                                   font=Font(bold=True),
                                   fill=PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af')))

            ws['P7'] = 'Travel expense middle'
            ws['P7'].fill = PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af'))
            ws['P7'].font = header_font
            ws['P7'].style = Style(border=Border(left=Side(style='thick', color=colors.BLACK),
                                                 right=Side(style='thick', color=colors.BLACK),
                                                 top=Side(style='thick', color=colors.BLACK),
                                                 bottom=Side(style='thick', color=colors.BLACK)),
                                   alignment=Alignment(wrap_text=True),
                                   font=Font(bold=True),
                                   fill=PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af')))

            ws['Q7'] = 'Travel expense large'
            ws['Q7'].fill = PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af'))
            ws['Q7'].font = header_font
            ws['Q7'].style = Style(border=Border(left=Side(style='thick', color=colors.BLACK),
                                                 right=Side(style='thick', color=colors.BLACK),
                                                 top=Side(style='thick', color=colors.BLACK),
                                                 bottom=Side(style='thick', color=colors.BLACK)),
                                   alignment=Alignment(wrap_text=True),
                                   font=Font(bold=True),
                                   fill=PatternFill(patternType='solid', fill_type='solid', fgColor=Color('ffe8af')))

            ws.row_dimensions[2].height = 20
            ws.row_dimensions[3].height = 20
            ws.row_dimensions[4].height = 20
            ws.row_dimensions[5].height = 20

            ws.row_dimensions[7].height = 45

            ws.column_dimensions['A'].width = 12
            ws.column_dimensions['H'].width = 20
            ws.column_dimensions['N'].width = 20

            n = 0
            base_date = d(1970, 1, 1)
            working_time_sum = 0.0
            for line in analytic_acc_lines:
                working_time_sum += line.unit_amount
                n += 1

                date = datetime.strptime(line.date, '%Y-%m-%d').date()
                delta = abs((base_date-date).days)
                color = 'e0eaff'
                if delta % 2 == 0:
                    color = '9bbcff'

                weekday = date.weekday()
                if weekday >= 5:  # sunday = 6
                    color = '999a9e'

                ws['A'+str(7+n)] = format_date(line.date) if line.date else ''
                ws['A'+str(7+n)].style = Style(font=Font(bold=True),
                                               alignment=Alignment(horizontal='center',
                                                                   wrap_text=True),
                                               fill=PatternFill(patternType='solid',
                                                                fill_type='solid',
                                                                fgColor=Color(color)),
                                               border=Border(left=Side(style='thick', color=colors.BLACK),
                                                             right=Side(style='thick', color=colors.BLACK),
                                                             top=Side(style='thin', color=colors.BLACK),
                                                             bottom=Side(style='thin', color=colors.BLACK)),
                                               )

                ws['B'+str(7+n)] = format_float_time(line.timesheet_start_time) if line.timesheet_start_time else ''
                ws['B'+str(7+n)].style = Style(alignment=Alignment(wrap_text=True),
                                               fill=PatternFill(patternType='solid',
                                                                fill_type='solid',
                                                                fgColor=Color(color)),
                                               border=Border(left=Side(style='thick', color=colors.BLACK),
                                                             right=Side(style='thick', color=colors.BLACK),
                                                             top=Side(style='thin', color=colors.BLACK),
                                                             bottom=Side(style='thin', color=colors.BLACK)),
                                               )

                ws['C'+str(7+n)] = format_float_time(line.timesheet_end_time) if line.timesheet_end_time else ''
                ws['C'+str(7+n)].style = Style(alignment=Alignment(wrap_text=True),
                                               fill=PatternFill(patternType='solid',
                                                                fill_type='solid',
                                                                fgColor=Color(color)),
                                               border=Border(left=Side(style='thick', color=colors.BLACK),
                                                             right=Side(style='thick', color=colors.BLACK),
                                                             top=Side(style='thin', color=colors.BLACK),
                                                             bottom=Side(style='thin', color=colors.BLACK)),
                                               )

                ws['D'+str(7+n)] = format_float_time(line.timesheet_break_amount) if line.timesheet_break_amount else ''
                ws['D'+str(7+n)].style = Style(alignment=Alignment(wrap_text=True),
                                               fill=PatternFill(patternType='solid',
                                                                fill_type='solid',
                                                                fgColor=Color(color)),
                                               border=Border(left=Side(style='thick', color=colors.BLACK),
                                                             right=Side(style='thick', color=colors.BLACK),
                                                             top=Side(style='thin', color=colors.BLACK),
                                                             bottom=Side(style='thin', color=colors.BLACK)),
                                               )

                ws['E'+str(7+n)] = format_float_time(line.unit_amount) if line.unit_amount else ''
                ws['E'+str(7+n)].style = Style(alignment=Alignment(wrap_text=True),
                                               fill=PatternFill(patternType='solid',
                                                                fill_type='solid',
                                                                fgColor=Color(color)),
                                               border=Border(left=Side(style='thick', color=colors.BLACK),
                                                             right=Side(style='thick', color=colors.BLACK),
                                                             top=Side(style='thin', color=colors.BLACK),
                                                             bottom=Side(style='thin', color=colors.BLACK)),
                                               )

                ws['F'+str(7+n)] = ''
                ws['F'+str(7+n)].style = Style(alignment=Alignment(wrap_text=True),
                                               fill=PatternFill(patternType='solid',
                                                                fill_type='solid',
                                                                fgColor=Color(color)),
                                               border=Border(left=Side(style='thick', color=colors.BLACK),
                                                             right=Side(style='thick', color=colors.BLACK),
                                                             top=Side(style='thin', color=colors.BLACK),
                                                             bottom=Side(style='thin', color=colors.BLACK)),
                                               )

                ws['G'+str(7+n)] = line.account_id.name if line.account_id else ''
                ws['G'+str(7+n)].style = Style(alignment=Alignment(wrap_text=True),
                                               fill=PatternFill(patternType='solid',
                                                                fill_type='solid',
                                                                fgColor=Color(color)),
                                               border=Border(left=Side(style='thick', color=colors.BLACK),
                                                             right=Side(style='thick', color=colors.BLACK),
                                                             top=Side(style='thin', color=colors.BLACK),
                                                             bottom=Side(style='thin', color=colors.BLACK)),
                                               )

                ws['H'+str(7+n)] = line.project_activity_id.name if line.project_activity_id else ''
                ws['H'+str(7+n)].style = Style(alignment=Alignment(wrap_text=True),
                                               fill=PatternFill(patternType='solid',
                                                                fill_type='solid',
                                                                fgColor=Color(color)),
                                               border=Border(left=Side(style='thick', color=colors.BLACK),
                                                             right=Side(style='thick', color=colors.BLACK),
                                                             top=Side(style='thin', color=colors.BLACK),
                                                             bottom=Side(style='thin', color=colors.BLACK)),
                                               )

                ws['I'+str(7+n)] = line.task_id.name if line.task_id else ''
                ws['I'+str(7+n)].style = Style(alignment=Alignment(wrap_text=True),
                                               fill=PatternFill(patternType='solid',
                                                                fill_type='solid',
                                                                fgColor=Color(color)),
                                               border=Border(left=Side(style='thick', color=colors.BLACK),
                                                             right=Side(style='thick', color=colors.BLACK),
                                                             top=Side(style='thin', color=colors.BLACK),
                                                             bottom=Side(style='thin', color=colors.BLACK)),
                                               )

                ws['J'+str(7+n)] = line.timesheet_travel_start if line.timesheet_travel_start else ''
                ws['J'+str(7+n)].style = Style(alignment=Alignment(wrap_text=True),
                                               fill=PatternFill(patternType='solid',
                                                                fill_type='solid',
                                                                fgColor=Color(color)),
                                               border=Border(left=Side(style='thick', color=colors.BLACK),
                                                             right=Side(style='thick', color=colors.BLACK),
                                                             top=Side(style='thin', color=colors.BLACK),
                                                             bottom=Side(style='thin', color=colors.BLACK)),
                                               )

                ws['K'+str(7+n)] = line.timesheet_travel_end if line.timesheet_travel_end else ''
                ws['K'+str(7+n)].style = Style(alignment=Alignment(wrap_text=True),
                                               fill=PatternFill(patternType='solid',
                                                                fill_type='solid',
                                                                fgColor=Color(color)),
                                               border=Border(left=Side(style='thick', color=colors.BLACK),
                                                             right=Side(style='thick', color=colors.BLACK),
                                                             top=Side(style='thin', color=colors.BLACK),
                                                             bottom=Side(style='thin', color=colors.BLACK)),
                                               )

                ws['L'+str(7+n)] = line.timesheet_is_driver if line.timesheet_is_driver else ''
                ws['L'+str(7+n)].style = Style(alignment=Alignment(wrap_text=True),
                                               fill=PatternFill(patternType='solid',
                                                                fill_type='solid',
                                                                fgColor=Color(color)),
                                               border=Border(left=Side(style='thick', color=colors.BLACK),
                                                             right=Side(style='thick', color=colors.BLACK),
                                                             top=Side(style='thin', color=colors.BLACK),
                                                             bottom=Side(style='thin', color=colors.BLACK)),
                                               )

                ws['M'+str(7+n)] = line.timesheet_vehicle_id.license_plate if line.timesheet_vehicle_id else ''
                ws['M'+str(7+n)].style = Style(alignment=Alignment(wrap_text=True),
                                               fill=PatternFill(patternType='solid',
                                                                fill_type='solid',
                                                                fgColor=Color(color)),
                                               border=Border(left=Side(style='thick', color=colors.BLACK),
                                                             right=Side(style='thick', color=colors.BLACK),
                                                             top=Side(style='thin', color=colors.BLACK),
                                                             bottom=Side(style='thin', color=colors.BLACK)),
                                               )

                ws['N'+str(7+n)] = line.timesheet_accommodation if line.timesheet_accommodation else ''
                ws['N'+str(7+n)].style = Style(alignment=Alignment(wrap_text=True),
                                               fill=PatternFill(patternType='solid',
                                                                fill_type='solid',
                                                                fgColor=Color(color)),
                                               border=Border(left=Side(style='thick', color=colors.BLACK),
                                                             right=Side(style='thick', color=colors.BLACK),
                                                             top=Side(style='thin', color=colors.BLACK),
                                                             bottom=Side(style='thin', color=colors.BLACK)),
                                               )

                ws['O'+str(7+n)] = '---'
                ws['O'+str(7+n)].style = Style(alignment=Alignment(wrap_text=True),
                                               fill=PatternFill(patternType='solid',
                                                                fill_type='solid',
                                                                fgColor=Color(color)),
                                               border=Border(left=Side(style='thick', color=colors.BLACK),
                                                             right=Side(style='thick', color=colors.BLACK),
                                                             top=Side(style='thin', color=colors.BLACK),
                                                             bottom=Side(style='thin', color=colors.BLACK)),
                                               )

                ws['P'+str(7+n)] = '---'
                ws['P'+str(7+n)].style = Style(alignment=Alignment(wrap_text=True),
                                               fill=PatternFill(patternType='solid',
                                                                fill_type='solid',
                                                                fgColor=Color(color)),
                                               border=Border(left=Side(style='thick', color=colors.BLACK),
                                                             right=Side(style='thick', color=colors.BLACK),
                                                             top=Side(style='thin', color=colors.BLACK),
                                                             bottom=Side(style='thin', color=colors.BLACK)),
                                               )

                ws['Q'+str(7+n)] = '---'
                ws['Q'+str(7+n)].style = Style(alignment=Alignment(wrap_text=True),
                                               fill=PatternFill(patternType='solid',
                                                                fill_type='solid',
                                                                fgColor=Color(color)),
                                               border=Border(left=Side(style='thick', color=colors.BLACK),
                                                             right=Side(style='thick', color=colors.BLACK),
                                                             top=Side(style='thin', color=colors.BLACK),
                                                             bottom=Side(style='thin', color=colors.BLACK)),
                                               )

            n += 1
            ws['A'+str(7+n)] = 'SUM'
            ws['A'+str(7+n)].style = Style(font=Font(bold=True),
                                           alignment=Alignment(horizontal='center',
                                                               wrap_text=True),
                                           border=Border(left=Side(style='thick', color=colors.BLACK),
                                                         right=Side(style='thick', color=colors.BLACK),
                                                         top=Side(style='thick', color=colors.BLACK),
                                                         bottom=Side(style='thick', color=colors.BLACK)),
                                           )

            ws['E'+str(7+n)] = format_float_time(working_time_sum)
            ws['E'+str(7+n)].style = Style(font=Font(bold=True),
                                           alignment=Alignment(wrap_text=True),
                                           border=Border(left=Side(style='thick', color=colors.BLACK),
                                                         right=Side(style='thick', color=colors.BLACK),
                                                         top=Side(style='thick', color=colors.BLACK),
                                                         bottom=Side(style='thick', color=colors.BLACK)),
                                           )


            ws['F'+str(7+n)] = '---'
            ws['F'+str(7+n)].style = Style(font=Font(bold=True),
                                           alignment=Alignment(wrap_text=True),
                                           border=Border(left=Side(style='thick', color=colors.BLACK),
                                                         right=Side(style='thick', color=colors.BLACK),
                                                         top=Side(style='thick', color=colors.BLACK),
                                                         bottom=Side(style='thick', color=colors.BLACK)),
                                           )

            n += 2
            ws.merge_cells('A'+str(7+n)+':F'+str(7+n+1))
            ws['A'+str(7+n)] = 'Signature of employee'
            ws['A'+str(7+n)].style = Style(alignment=Alignment(vertical='top', horizontal='left'),
                                           border=Border(left=Side(style='thick', color=colors.BLACK),
                                                         top=Side(style='thick', color=colors.BLACK)))
            ws['F'+str(7+n)].style = Style(border=Border(right=Side(style='thick', color=colors.BLACK),
                                                         top=Side(style='thick', color=colors.BLACK)))
            ws['F'+str(7+n+1)].style = Style(border=Border(right=Side(style='thick', color=colors.BLACK),
                                                           bottom=Side(style='thick', color=colors.BLACK)))


            n += 2
            ws.merge_cells('A'+str(7+n)+':F'+str(7+n+1))
            ws['A'+str(7+n)] = 'Signature of line manager'
            ws['A'+str(7+n)].style = Style(alignment=Alignment(vertical='top', horizontal='left'),
                                           border=Border(left=Side(style='thick', color=colors.BLACK),
                                                         top=Side(style='thick', color=colors.BLACK)))
            ws['F'+str(7+n)].style = Style(border=Border(right=Side(style='thick', color=colors.BLACK),
                                                         top=Side(style='thick', color=colors.BLACK)))
            ws['F'+str(7+n+1)].style = Style(border=Border(right=Side(style='thick', color=colors.BLACK),
                                                           bottom=Side(style='thick', color=colors.BLACK)))

            n += 2
            ws.merge_cells('A'+str(7+n)+':F'+str(7+n+1))
            ws['A'+str(7+n)] = 'Signature of executive employee / managing director'
            ws['A'+str(7+n)].style = Style(alignment=Alignment(vertical='top', horizontal='left'),
                                           border=Border(left=Side(style='thick', color=colors.BLACK),
                                                         top=Side(style='thick', color=colors.BLACK)))
            ws['F'+str(7+n)].style = Style(border=Border(right=Side(style='thick', color=colors.BLACK),
                                                         top=Side(style='thick', color=colors.BLACK)))
            ws['F'+str(7+n+1)].style = Style(border=Border(right=Side(style='thick', color=colors.BLACK),
                                                           bottom=Side(style='thick', color=colors.BLACK)))
            ws['A'+str(7+n+1)].style = Style(border=Border(left=Side(style='thick', color=colors.BLACK),
                                                           bottom=Side(style='thick', color=colors.BLACK)))



            # FORMATIRANJE SHEETA

            # ws.column_dimensions['A'].width = 23
            # ws.column_dimensions['B'].width = 25
            # ws.column_dimensions['C'].width = 15
            # ws.column_dimensions['D'].width = 42


        buf = cStringIO.StringIO()
        wb.save(buf)
        buf.seek(0)
        out = base64.encodestring(buf.read())
        buf.close()

        self.write({'state': 'get',
                                  'data': out,
                                  'name': 'employee_timesheets_'+dict(MONTHS).get(month)+'_'+dict(YEARS).get(year)+'.xlsx'})
        return {
            'type': 'ir.actions.act_window',
            'res_id': self[0].id,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'employee.timesheet.generator',
            'target': 'new',
            'context': self.env.context,
        }
