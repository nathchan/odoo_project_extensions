# -*- coding: utf-8 -*-

from openerp import models, fields, api

class ProjectActivityCategory(models.Model):
    _name = 'project.activity.category'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', requiered=True)
    info = fields.Text('Description')
    useful = fields.Boolean('Useful')

class ProjectActivity(models.Model):
    _name = 'project.activity'

    name = fields.Char('Name', required=True)
    category_id = fields.Many2one('project.activity.category', 'Category', required=True)
    category_code = fields.Char('Category code', related='category_id.code', readonly=True)
    info = fields.Text('Description')




