# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectActivity(models.Model):
    _name = 'project.activity'

    name = fields.Char('Name', required=True)
    info = fields.Text('Description')
    category = fields.Selection([('effective', 'Effective'), ('ineffective', 'Ineffective')], 'Category')
    on_site_activity = fields.Boolean('On site activity')
    show_on_sap_report = fields.Boolean('Show on SAP report')




