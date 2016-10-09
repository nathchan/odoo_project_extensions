# -*- coding: utf-8 -*-

from openerp import models, fields, api


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.onchange('project_activity_id')
    def _change_project_activity(self):
        if self.project_activity_id:
            self.name = self.project_activity_id.name

    project_activity_id = fields.Many2one('project.activity', 'Activity')

