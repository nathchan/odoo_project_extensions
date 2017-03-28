# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectActivityWorkPackage(models.Model):
    _name = 'project.activity.work.package'

    @api.multi
    def _compute_filter_timesheet_selection_by_account_id(self):
        for rec in self:
            rec.filter_timesheet_selection_by_account_id = '---'

    def _search_filter_timesheet_selection_by_account_id(self, operator, value):
        res_ids = []
        account_id = self.env['account.analytic.account'].browse(value)
        account_wp_ids = account_id.work_package_line_ids
        if operator == '=' and len(account_wp_ids):
            operator = 'in'
            res_ids = [item.work_package_id.id for item in account_wp_ids]
        else:
            operator = 'in'
            res_ids = [item.id for item in self.search([])]
        return [('id', operator, res_ids)]

    name = fields.Char('Name', required=True)
    info = fields.Text('Description')
    sap_report_task_sufix = fields.Char('Task sufix default')
    sap_report_service_number = fields.Char('Service number default')

    filter_timesheet_selection_by_account_id = fields.Char(compute=_compute_filter_timesheet_selection_by_account_id,
                                                           search=_search_filter_timesheet_selection_by_account_id)
