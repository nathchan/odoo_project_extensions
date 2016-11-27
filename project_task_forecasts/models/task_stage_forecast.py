# -*- coding: utf-8 -*-

from openerp import models, fields, api
import datetime

class ProjectTaskMilestoneForecast(models.Model):
    _name = 'project.task.milestone.forecast'

    @api.multi
    def _get_default_duration(self):
        for rec in self:
            rec.duration_days = rec.milestone_id.duration

    @api.multi
    @api.depends('forecast_date', 'duration_forecast')
    def _compute_forecast_start_date(self):
        for rec in self:
            if rec.forecast_date:
                business_days_to_add = rec.duration_forecast
                current_date = datetime.datetime.strptime(rec.forecast_date, '%Y-%m-%d')
                while business_days_to_add > 0:
                    current_date -= datetime.timedelta(days=1)
                    weekday = current_date.weekday()
                    if weekday >= 5: # sunday = 6
                        continue
                    business_days_to_add -= 1
                rec.forecast_start_date = current_date.strftime('%Y-%m-%d')

    @api.multi
    def _get_name(self):
        for rec in self:
            rec.name = ''
            if rec.milestone_id:
                rec.name += 'Milestone ' + str(rec.milestone_id.name)
            if rec.task_id:
                rec.name += ' - Task ' + str(rec.task_id.name)

    @api.multi
    def _compute_issue_count(self):
        for obj in self:
            if obj.task_id:
                obj.issue_count = self.env['project.issue'].search_count([('task_id', '=', obj.task_id.id)])
            else:
                obj.issue_count = 0

    issue_count = fields.Integer('Issue Count', compute=_compute_issue_count)
    project_id = fields.Many2one('project.project', 'Project', required=True)
    task_id = fields.Many2one('project.task', 'Task', required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence', related='milestone_id.sequence', store=True)

    milestone_id = fields.Many2one('project.milestone', 'Milestone', required=True, ondelete='restrict')

    forecast_date = fields.Date('Forecast end date')
    actual_date = fields.Date('Actual end date')

    name = fields.Char('Name', compute=_get_name)

    duration_forecast = fields.Integer('Duration forecast', default=_get_default_duration)
    forecast_start_date = fields.Date('Forecast start date', compute=_compute_forecast_start_date, store=True)

    _sql_constraints = [
        ('unique_task_milestone', 'unique(task_id, milestone_id)', 'Combination of task and milestone must be unique!')
    ]