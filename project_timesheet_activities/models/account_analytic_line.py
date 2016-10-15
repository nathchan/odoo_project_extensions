# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp import exceptions as e



class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.onchange('project_activity_id')
    def _change_project_activity(self):
        if self.project_activity_id:
            self.name = self.project_activity_id.name

    @api.onchange('timesheet_start_time', 'timesheet_end_time', 'timesheet_break_amount')
    def _change_times_to_calc_total(self):
        self.unit_amount = self.timesheet_end_time - self.timesheet_start_time - self.timesheet_break_amount

    project_activity_id = fields.Many2one('project.activity', 'Activity')
    useful = fields.Boolean('Useful', related='project_activity_id.category_id.useful', store=True)

    timesheet_vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')

    timesheet_start_time = fields.Float('Start time')
    timesheet_end_time = fields.Float('End time')
    timesheet_break_amount = fields.Float('Break')

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
        if self.timesheet_break_amount > self.unit_amount:
            raise e.ValidationError('Break must be less than total hours.')
        if self.timesheet_break_amount < 0:
            raise e.ValidationError('Break must be non negative.')
