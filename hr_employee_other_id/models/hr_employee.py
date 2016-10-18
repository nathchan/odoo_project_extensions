# -*- coding: utf-8 -*-

from openerp import models, fields, api


class Employee(models.Model):
    _inherit = 'hr.employee'

    other_id = fields.Char('Other ID')
