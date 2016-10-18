# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectIssueSubcategory(models.Model):
    _name = 'project.issue.subcategory'

    name = fields.Char('Name', required=True)
    category_id = fields.Many2one('project.issue.category', 'Category', required=True)
    info = fields.Text('Description')
