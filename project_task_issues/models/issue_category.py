# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectIssueCategory(models.Model):
    _name = 'project.issue.category'

    name = fields.Char('Name', required=True)
    info = fields.Text('Description')
    subcategory_ids = fields.One2many('project.issue.subcategory', 'category_id', 'Subcategories')
