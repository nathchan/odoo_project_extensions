# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectCheckListActivity(models.Model):
    _name = 'project.check.list.activity'
    _order = 'sequence_order'

    sequence_order = fields.Integer('Sequence')
    name = fields.Char('Name', required=True)
    info = fields.Text('Description')
