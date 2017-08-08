# -*- coding: utf-8 -*-

from openerp import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    READONLY_STATES = {
        'done': [('readonly', True)],
        'cancel': [('readonly', True)]
    }

    @api.multi
    @api.depends('analytic_account_id')
    def _compute_project_use_task_issues(self):
        for rec in self:
            rec.analytic_account_id_use_issues = rec.analytic_account_id.use_issues
            rec.analytic_account_id_use_tasks = rec.analytic_account_id.use_tasks

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic account', required=True, states=READONLY_STATES)
    analytic_account_id_use_tasks = fields.Boolean(compute=_compute_project_use_task_issues)
    analytic_account_id_use_issues = fields.Boolean(compute=_compute_project_use_task_issues)
    task_id = fields.Many2one('project.task', 'Task', states=READONLY_STATES)