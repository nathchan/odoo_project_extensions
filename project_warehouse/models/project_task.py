# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools, exceptions as ex


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.multi
    def return_action_to_open_inventory(self):
        self.ensure_one()
        location_search = '%s/%s' % (self.project_id.name, self.name)
        res = {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.quant',
            'view_type': 'form',
            'view_mode': 'tree',
            'domain': "[('location_id.complete_name', 'ilike', '%s')]" % location_search
        }
        return res
