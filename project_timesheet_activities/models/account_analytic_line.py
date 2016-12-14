# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp import exceptions as e



class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

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
    def _compute_project_use_task_issues(self):
        self.account_id_use_issues = self.account_id.use_issues
        self.account_id_use_tasks = self.account_id.use_tasks

    account_id_use_tasks = fields.Boolean(compute=_compute_project_use_task_issues)
    account_id_use_issues = fields.Boolean(compute=_compute_project_use_task_issues)

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

    # sheet_id = fields.Many2one('hr_timesheet_sheet.sheet', string='Sheet', ondelete="cascade")

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
