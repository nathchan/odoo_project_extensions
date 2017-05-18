# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions as ex


class MilestoneTemplate(models.Model):
    _inherit = 'project.milestone.template'

    milestone_ids = fields.One2many('project.milestone', 'project_id', 'Milestones')
    project_id = fields.Many2one('project.project', 'Project')

    @api.one
    def apply_milestones_template(self):
        err_msgs = []
        for task in self.env['project.task'].search([('milestone_template_id', '=', self.id)]):
            ms = task.milestone_ids.sorted(lambda x: x.sequence_order)[0]
            try:
                ms.calculate_forecast()
            except Exception as e:
                err_msgs.append(e.name)

        if len(err_msgs) > 0:
            raise ex.UserError('\n\n\n'.join(err_msgs))
