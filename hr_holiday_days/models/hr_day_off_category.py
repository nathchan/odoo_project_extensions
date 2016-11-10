# -*- coding: utf-8 -*-

from openerp import models, fields, api

class HrDayOffCategory(models.Model):
    _name = 'hr.day.off.category'

    name = fields.Char('Name', required=True)
    info = fields.Text('Description')
