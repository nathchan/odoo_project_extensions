# -*- coding: utf-8 -*-

from openerp import models, fields, api
import datetime


class ProjectTaskGroup(models.Model):
    _name = 'project.task.group'

    name = fields.Char('Name', required=True)
    info = fields.Text('Description')
    task_ids = fields.One2many('project.task', 'task_group_id', 'Tasks', readonly=True)
