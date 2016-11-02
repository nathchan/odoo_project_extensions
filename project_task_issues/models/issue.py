# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    category_id = fields.Many2one('project.issue.category', 'Category')
    subcategory_id = fields.Many2one('project.issue.subcategory', 'Subcategory', context="{'default_category_id': category_id}", domain="[('category_id','=',category_id)]")
    solution = fields.Text('Solution')

    @api.onchange('subcategory_id')
    def change_subcategory(self):
        self.category_id = self.subcategory_id.category_id
