# -*- coding: utf-8 -*-

from openerp import models, fields


class ProjectTask(models.Model):
    _inherit = 'project.task'

    forecast_ids = fields.One2many('project.task.stage.forecast', 'task_id', 'Stages forecast')
    stage_progress = fields.Float('Stage progress', readonly=True)


class ProjectTaskStagesForecast(models.Model):
    _name = 'project.task.stage.forecast'

    project_id = fields.Many2one('project.project', 'Project', related='task_id.project_id')
    task_id = fields.Many2one('project.task', 'Task')
    sequence = fields.Integer('Sequence', related='stage_id.sequence')
    stage_id = fields.Many2one('project.task.type', 'Stage', domain="[('project_ids', '=', project_id)])")
    forecast_date = fields.Date('Forecast date')
    actual_date = fields.Date('Actual date')

