# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectTaskPackage(models.Model):
    _name = 'project.task.package'

    name = fields.Char('Name', required=True)
    info = fields.Text('Description')