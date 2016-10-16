# -*- coding: utf-8 -*-

from openerp import models, fields, api
import datetime

class ProjectTaskTypeProcess(models.Model):
    _name = 'project.task.stage.process'
    _order = 'sequence'

    name = fields.Char('Name', required=True)
    info = fields.Text('Description')
    sequence = fields.Integer('Sequence', default=10)
    stage_id = fields.Many2one('project.task.type', 'Stage', required=True)
