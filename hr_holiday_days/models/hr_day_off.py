# -*- coding: utf-8 -*-

from openerp import models, fields, api

class HrDayOff(models.Model):
    _name = 'hr.day.off'

    @api.multi
    def _compute_name(self):
        for rec in self:
            rec.name = rec.date + ' - ' + rec.category_id.name

    name = fields.Char('Name', compute=_compute_name)
    date = fields.Date('Date', required=True)
    category_id = fields.Many2one('hr.day.off.category', 'Category', required=True)
    info = fields.Text('Description')

    _sql_constraints = [('Unique date', 'unique(date)', 'Selected date already exists as day off.')]