# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    @api.depends('category_id.name')
    def _compute_category_name(self):
        if self.category_id:
            self.category_name = self.category_id.name

    category_id = fields.Many2one('project.issue.category', 'Category')
    category_name = fields.Char('Category Name', compute=_compute_category_name)
    subcategory_id = fields.Many2one('project.issue.subcategory', 'Subcategory', context="{'default_category_id': category_id}", domain="[('category_id','=',category_id)]")
    solution = fields.Text('Solution')

    @api.onchange('subcategory_id')
    def change_subcategory(self):
        self.category_id = self.subcategory_id.category_id
