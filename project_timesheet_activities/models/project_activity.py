# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectActivity(models.Model):
    _name = 'project.activity'

    @api.multi
    def _compute_filter_activities(self):
        for rec in self:
            rec.filter_activities = '---'

    def _search_filter_activities(self, operator, value):
        if operator == '=' and value == 'General':
            operator = 'in'
            res_ids = [item.id for item in self.search([('is_general_activity', '=', True)])]
        elif operator == '=' and self.env['project.project'].search([('name', '=', value)], count=True) > 0:
            operator = 'in'
            res_ids = [item.id for item in self.search([('is_on_project_activity', '=', True)])]
        else:
            operator = 'in'
            res_ids = [item.id for item in self.search([])]
        return [('id', operator, res_ids)]

    name = fields.Char('Name', required=True)
    info = fields.Text('Description')
    category = fields.Selection([('effective', 'Effective'), ('ineffective', 'Ineffective')], 'Category')
    on_site_activity = fields.Boolean('On site activity')
    show_on_sap_report = fields.Boolean('Show on SAP report')
    sap_report_sufix = fields.Char('SAP sufix')
    is_general_activity = fields.Boolean('Is general activity')
    is_on_project_activity = fields.Boolean('Is on project activity')
    filter_activities = fields.Char(compute=_compute_filter_activities, search=_search_filter_activities)






