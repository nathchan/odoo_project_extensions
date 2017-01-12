# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools
from openerp import exceptions as e
import datetime
import math


def format_float_time_str(time):
    x = math.modf(time)
    decimal = abs(int(x[0] * 61))
    whole = abs(int(x[1]))
    if decimal >= 60:
        decimal -= 60
        whole += 1
    res = str(whole) if whole >= 10 else '0'+str(whole)
    res += ':'
    res += str(decimal) if decimal >= 10 else '0'+str(decimal)
    res += ':00'
    return res


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    _order = 'date DESC'

    @api.onchange('project_activity_id')
    def _change_project_activity(self):
        if self.project_activity_id:
            self.name = self.project_activity_id.name
        else:
            self.name = self.account_id.name

    @api.onchange('account_id')
    def _change_account_id(self):
        self.name = self.account_id.name
        if(self.account_id.name == 'Feiertag'):
            self.timesheet_start_time = 9.0
            self.timesheet_end_time = 15.695


    @api.onchange('unit_amount', 'timesheet_start_time', 'timesheet_end_time', 'timesheet_break_amount')
    def _change_times_to_calc_total(self):
        self.unit_amount = self.timesheet_end_time - self.timesheet_start_time - self.timesheet_break_amount

    def _get_default_department(self):
        emp = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        dep = emp.department_id
        return dep

    @api.one
    @api.depends('account_id')
    def _compute_project_use_task_issues_name(self):
        self.account_id_use_issues = self.account_id.use_issues
        self.account_id_use_tasks = self.account_id.use_tasks
        self.account_id_name = self.account_id.name

    @api.multi
    @api.depends('date')
    def _compute_color_record(self):
        for rec in self:
            if rec.date:
                date = datetime.datetime.strptime(rec.date, tools.DEFAULT_SERVER_DATE_FORMAT)
                if (date - datetime.datetime(1900, 1, 1)).days % 2 == 0:
                    rec.timesheet_color_record = True
                else:
                    rec.timesheet_color_record = False

    @api.multi
    @api.depends('task_id.user_id')
    def _compute_task_assigned_to(self):
        for rec in self:
            if rec.task_id and rec.task_id.user_id:
                rec.timesheet_task_assigned_to = rec.task_id.user_id

    account_id_use_tasks = fields.Boolean(compute=_compute_project_use_task_issues_name)
    account_id_use_issues = fields.Boolean(compute=_compute_project_use_task_issues_name)
    account_id_name = fields.Char(compute=_compute_project_use_task_issues_name)

    project_activity_id = fields.Many2one('project.activity', 'Activity')
    timesheet_activity_category = fields.Selection([('effective', 'Effective'), ('ineffective', 'Ineffective')],
                                               string='Effectiveness category',
                                               related='project_activity_id.category',
                                               store=True)

    timesheet_analytic_account_category = fields.Selection([('on_project', 'On project'),
                                                            ('not_on_project', 'Not on project'),
                                                            ('not_in_production', 'Not in production')],
                                                           string='Production category',
                                                           related='account_id.category',
                                                           store=True)
    timesheet_on_site_activity = fields.Boolean('On site activity', related='project_activity_id.on_site_activity')

    timesheet_department_id = fields.Many2one('hr.department', 'Department', default=_get_default_department)

    timesheet_travel_start = fields.Char('Start travel (Place/Postcode)')
    timesheet_travel_end = fields.Char('End travel (Place/Postcode)')
    timesheet_is_driver = fields.Selection([('no', 'No'), ('yes', 'Yes')], 'Driver?', default='no')
    timesheet_accommodation = fields.Char('Accommodation')
    timesheet_vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')

    timesheet_start_time = fields.Float('Start time')
    timesheet_end_time = fields.Float('End time')
    timesheet_break_amount = fields.Float('Break')
    timesheet_comment = fields.Char('Comment', size=20)

    timesheet_approved_status = fields.Selection([('new', 'New'),
                                                  ('draft', 'Waiting Approval'),
                                                  ('approved', 'Approved'),
                                                  ('refused', 'Refused')], 'Approval status', default='new')

    timesheet_color_record = fields.Boolean('Color record', compute=_compute_color_record)
    timesheet_task_assigned_to = fields.Many2one('res.users', 'Task Assigned to', compute=_compute_task_assigned_to, store=True)

    @api.multi
    def approve(self):
        for rec in self:
            if (rec.timesheet_task_assigned_to.id == self.env.user.id) or self.env.user._has_group(self.env.cr, self.env.user.id, 'project_timesheet_activities.group_hr_timesheet_rollout_manager'):
                rec.timesheet_approved_status = 'approved'

    @api.multi
    def refuse(self):
        for rec in self:
            if (rec.timesheet_task_assigned_to.id == self.env.user.id) or self.env.user._has_group(self.env.cr, self.env.user.id, 'project_timesheet_activities.group_hr_timesheet_rollout_manager'):
                rec.timesheet_approved_status = 'refused'


    @api.one
    @api.constrains('timesheet_start_time', 'timesheet_end_time')
    def _check_start_end_time(self):
        if (self.timesheet_start_time != 0) and (self.timesheet_end_time != 0):
            if self.timesheet_start_time >= self.timesheet_end_time:
                raise e.ValidationError('Start time must be before end time.')
            if (self.timesheet_start_time < 0) or (self.timesheet_end_time < 0):
                raise e.ValidationError('Start and end time must be non negative.')

    @api.one
    @api.constrains('timesheet_break_amount')
    def _check_break_amount(self):
        if self.unit_amount <= 0:
            raise e.ValidationError('Total hours must be non negative.')
        if self.timesheet_break_amount < 0:
            raise e.ValidationError('Break must be non negative.')

    @api.multi
    def write(self, vals):
        if self.timesheet_approved_status in ['draft', 'approved']:
            if len(vals) == 1 and 'timesheet_approved_status' in vals:
                old_state = self.timesheet_approved_status
                super(AccountAnalyticLine, self).write(vals)
                if old_state != 'approved' and vals['timesheet_approved_status'] == 'approved':
                    self.sheet_id.message_post(self.env.user.name+' Approved: '+ ', '.join([self.date, self.account_id.name, self.project_activity_id.name or '', format_float_time_str(self.unit_amount)]))
                elif old_state != 'refused' and vals['timesheet_approved_status'] == 'refused':
                    self.sheet_id.message_post(self.env.user.name+' Refused: '+ ', '.join([self.date, self.account_id.name, self.project_activity_id.name or '', format_float_time_str(self.unit_amount)]))
                if vals['timesheet_approved_status'] == 'approved':
                    sheet = self.env['hr_timesheet_sheet.sheet'].search([('id', '=', self.sheet_id.id)], limit=1)
                    if len(sheet.timesheet_ids) == sheet.timesheet_ids.filtered(lambda r: r.timesheet_approved_status == 'approved'):
                        sheet.approved_status = 'approved'
                elif vals['timesheet_approved_status'] == 'refused':
                    sheet = self.env['hr_timesheet_sheet.sheet'].search([('id', '=', self.sheet_id.id)], limit=1)
                    if len(sheet.timesheet_ids) == sheet.timesheet_ids.filtered(lambda r: r.timesheet_approved_status == 'refused'):
                        sheet.approved_status = 'refused'
            else:
                raise e.ValidationError('You can not edit approved timesheet line.')
        else:
            if 'timesheet_approved_status' in vals and vals['timesheet_approved_status'] in ['approved', 'refused']:
                old_state = self.timesheet_approved_status
                super(AccountAnalyticLine, self).write(vals)
                if old_state != 'approved' and vals['timesheet_approved_status'] == 'approved':
                    self.sheet_id.message_post(self.env.user.name+' Approved: '+ ', '.join([self.date, self.account_id.name, self.project_activity_id.name or '', format_float_time_str(self.unit_amount)]))
                elif old_state != 'refused' and vals['timesheet_approved_status'] == 'refused':
                    self.sheet_id.message_post(self.env.user.name+' Refused: '+ ', '.join([self.date, self.account_id.name, self.project_activity_id.name or '', format_float_time_str(self.unit_amount)]))
                if vals['timesheet_approved_status'] == 'approved':
                    sheet = self.env['hr_timesheet_sheet.sheet'].search([('id', '=', self.sheet_id.id)], limit=1)
                    if len(sheet.timesheet_ids) == sheet.timesheet_ids.filtered(lambda r: r.timesheet_approved_status == 'approved'):
                        sheet.approved_status = 'approved'
                elif vals['timesheet_approved_status'] == 'refused':
                    sheet = self.env['hr_timesheet_sheet.sheet'].search([('id', '=', self.sheet_id.id)], limit=1)
                    if len(sheet.timesheet_ids) == sheet.timesheet_ids.filtered(lambda r: r.timesheet_approved_status == 'refused'):
                        sheet.approved_status = 'refused'
            else:
                super(AccountAnalyticLine, self).write(vals)
