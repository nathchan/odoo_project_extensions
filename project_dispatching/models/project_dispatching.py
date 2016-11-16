# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools, exceptions as e
import datetime


class ProjectDispatching(models.Model):
    _name = 'project.dispatching'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    @api.multi
    def _compute_name(self):
        for rec in self:
            rec.name = rec.department_id.name + ' - ' + rec.task_id.name

    def _get_default_completition(self):
        return 0

    @api.onchange('analytic_account_id', 'task_id')
    def _onchange_department_project_task(self):
        if self.analytic_account_id and self.task_id:
            query = 'select max(percent_complete) from project_dispatching where analytic_account_id=%s and task_id=%s'
            self.env.cr.execute(query, (self.analytic_account_id.id, self.task_id.id,))
            res = self.env.cr.fetchone()
            if res and res[0] and res[0]>0:
                self.percent_complete = res[0]

    name = fields.Char('Name', compute=_compute_name)
    all_day = fields.Boolean('All day', readonly="True", default=True)
    department_id = fields.Many2one('hr.department', 'Department', required=True, track_visibility='onchange')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Field of activity', required=True, track_visibility='onchange')
    analytic_account_id_use_tasks = fields.Boolean(related='analytic_account_id.use_tasks')
    task_id = fields.Many2one('project.task', 'Task', track_visibility='onchange')
    date_start = fields.Date('Date from', track_visibility='onchange')
    date_stop = fields.Date('Date to', track_visibility='onchange')
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', track_visibility='onchange')
    percent_complete = fields.Selection([(0, '0 %'),
                                        (25, '25 %'),
                                        (50, '50 %'),
                                        (75, '75 %'),
                                        (100, '100 %')], string='% Complete', track_visibility='onchange', default=_get_default_completition)

    @api.constrains('date_start', 'date_stop')
    def _check_dates(self):
        start = datetime.datetime.strptime(self.date_start, tools.DEFAULT_SERVER_DATE_FORMAT) if self.date_start else False
        end = datetime.datetime.strptime(self.date_stop, tools.DEFAULT_SERVER_DATE_FORMAT) if self.date_stop else False
        if start and end:
            if start > end:
                raise e.ValidationError('Starting date must be lower than ending date.')
