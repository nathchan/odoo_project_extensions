# -*- coding: utf-8 -*-

from openerp import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
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

    @api.multi
    def _get_destination_location(self):
        self.ensure_one()
        if self.dest_address_id:
            return self.dest_address_id.property_stock_customer.id

        if self.analytic_account_id and self.task_id:
            search_name = '%s/%s' % (self.analytic_account_id.name, self.task_id.name)
            task_location = self.env['stock.location'].search([('complete_name', 'ilike', search_name)], limit=1)
            if task_location:
                return task_location.id

        return self.picking_type_id.default_location_dest_id.id

    @api.model
    def _prepare_picking(self):
        res = super(PurchaseOrder, self)._prepare_picking()
        res['analytic_account_id'] = self.analytic_account_id.id
        res['task_id'] = self.task_id.id
        return res


    # napraviti skladiste terasis
    # napraviti lokacije 'view' za svaki projekat
    # unutar projekta lokacije su: balk, V123, C145
