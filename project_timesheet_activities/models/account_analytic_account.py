# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp import exceptions as e



class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    category = fields.Selection([('on_project', 'On project'),
                                 ('not_on_project', 'Not on project'),
                                 ('not_in_production', 'Not in production')], 'Category')

    choose_on_timesheets = fields.Boolean('Display as an option in timesheets')

    # to delete, but first needs to be checked for existing references
    sap_report_category = fields.Selection([('sa', '7332'), ('cw', '7331')], 'SAP report category')

    work_package_line_ids = fields.One2many('project.activity.work.package.line', 'account_id', 'Work packages')
