# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    @api.multi
    @api.depends('milestone_id')
    def _compute_template_milestone(self):
        for rec in self:
            rec.template_milestone_id = False
            if rec.milestone_id:
                rec.template_milestone_id = rec.milestone_id.milestone_id

    milestone_id = fields.Many2one('project.task.milestone.forecast', 'Milestone', domain="[('task_id', '=', task_id)]")
    template_milestone_id = fields.Many2one('project.milestone', 'Milestone', compute=_compute_template_milestone, store=True)
