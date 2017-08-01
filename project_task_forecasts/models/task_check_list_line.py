# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectTaskCheckListLine(models.Model):
    _name = 'project.task.check.list.line'
    _order = 'sequence_order'

    sequence_order = fields.Integer('Sequence', related='check_list_activity_id.sequence_order', store=True)
    task_id = fields.Many2one('project.task', 'Task', required=True)
    check_list_activity_id = fields.Many2one('project.check.list.activity', 'Activity', required=True)
    forecast_date = fields.Date('Forecast date')
    actual_date = fields.Date('Actual date')

    _sql_constraints = [
        ('unique_task_check_list_activity', 'unique(task_id, check_list_activity_id)', 'Combination of task and check list activity must be unique!')
    ]
