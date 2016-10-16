# -*- coding: utf-8 -*-

from openerp import models, fields


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    duration_forecast = fields.Integer('Duration forecast')
    process_ids = fields.One2many('project.task.stage.process', 'stage_id', 'Child Processes')
