# -*- coding: utf-8 -*-

from openerp import models, fields, api
import datetime

class ProjectTaskStagesForecast(models.Model):
    _name = 'project.task.stage.forecast'
    _rec_name = 'task_id'

    @api.multi
    def _get_default_duration(self):
        for rec in self:
            rec.duration_days = rec.stage_id.duration_forecast

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
            rec.name = rec.stage_id.name

    project_id = fields.Many2one('project.project', 'Project', required=True)
    task_id = fields.Many2one('project.task', 'Task', required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence', related='stage_id.sequence', store=True)
    stage_id = fields.Many2one('project.task.type', 'Stage', required=True, ondelete='cascade')
    forecast_date = fields.Date('Forecast end date')
    actual_date = fields.Date('Actual end date')

    name = fields.Char('Name', compute=_get_name)

    duration_forecast = fields.Integer('Duration forecast', default=_get_default_duration)
    forecast_start_date = fields.Date('Forecast start date', compute=_compute_forecast_start_date, store=True)

    _sql_constraints = [
        ('unique_task_stage', 'unique(task_id, stage_id)', 'Combination of task and milestone must be unique!')
    ]