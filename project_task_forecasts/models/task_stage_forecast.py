# -*- coding: utf-8 -*-

from openerp import models, fields, api
import datetime

class ProjectTaskStagesForecast(models.Model):
    _name = 'project.task.stage.forecast'
    _rec_name = 'task_id'

    project_id = fields.Many2one('project.project', 'Project', required=True)
    task_id = fields.Many2one('project.task', 'Task', required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence', related='stage_id.sequence', store=True)
    stage_id = fields.Many2one('project.task.type', 'Stage', required=True, ondelete='cascade')
    forecast_date = fields.Date('Forecast date')
    actual_date = fields.Date('Actual date')

    _sql_constraints = [
        ('unique_task_stage', 'unique(task_id, stage_id)', 'Combination of task and milestone must be unique!')
    ]