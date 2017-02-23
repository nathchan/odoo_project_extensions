# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectTaskPriority(models.Model):
    _name = 'project.task.priority'

    name = fields.Char('Name', required=True)
    info = fields.Text('Description')
