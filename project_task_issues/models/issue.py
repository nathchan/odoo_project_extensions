# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    @api.depends('category_id.name')
    def _compute_category_name(self):
        if self.category_id:
            self.category_name = self.category_id.name

    @api.depends('active')
    @api.multi
    def _compute_status(self):
        for rec in self:
            if rec.active is True:
                rec.status = 'opened'
            else:
                rec.status = 'closed'

    category_id = fields.Many2one('project.issue.category', 'Category')
    category_name = fields.Char('Category Name', compute=_compute_category_name)
    subcategory_id = fields.Many2one('project.issue.subcategory', 'Subcategory', context="{'default_category_id': category_id}", domain="[('category_id','=',category_id)]")
    solution = fields.Text('Solution')
    status = fields.Selection([('opened', 'Opened'), ('closed', 'Closed')], 'Status', compute=_compute_status, store=True)

    @api.onchange('subcategory_id')
    def change_subcategory(self):
        self.category_id = self.subcategory_id.category_id
