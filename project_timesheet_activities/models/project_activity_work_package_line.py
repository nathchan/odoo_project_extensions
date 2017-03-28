# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectActivityWorkPackageLine(models.Model):
    _name = 'project.activity.work.package.line'

    account_id = fields.Many2one('account.analytic.account', 'Analytic account', required=True)
    work_package_id = fields.Many2one('project.activity.work.package', 'Work package', required=True)
    sap_report_task_prefix = fields.Char('Task prefix')
    sap_report_task_sufix = fields.Char('Task sufix')
    sap_report_service_number = fields.Char('Service number')

    _sql_constraints = [ ('unique_project_wp', 'unique(account_id, work_package_id)', 'Combination of Analytic account and Work package must be unique.') ]
