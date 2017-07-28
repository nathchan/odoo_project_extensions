# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions as e


class MilestoneTemplateLine(models.Model):
    _name = 'project.milestone.template.line'
    _order = 'sequence_order'

    @api.onchange('project_id')
    def _onchange_milestone_template(self):
        self.project_id = self.milestone_template_id.project_id

    @api.onchange('milestone_id')
    def _onchange_milestone(self):
        if self.milestone_id:
            self.duration = self.milestone_id.duration
            self.sequence_order = self.milestone_id.sequence_order
            self.predecessor_milestone_ids = self.milestone_id.predecessor_milestone_ids

    milestone_template_id = fields.Many2one('project.milestone.template', string='Template', required=True)
    project_id = fields.Many2one('project.project', 'Project')
    milestone_id = fields.Many2one('project.milestone', 'Milestone', required=True)
    predecessor_milestone_ids = fields.Many2many('project.milestone', string='Predecessors')
    sequence_order = fields.Integer('Sequence', required=True)
    duration = fields.Integer('Duration in days', required=True)

    @api.constrains('milestone_id', 'milestone_template_id')
    def default_project_template_constrains(self):
        if self.milestone_id and self.milestone_template_id:
            if self.search([('milestone_id', '=', self.milestone_id.id), ('milestone_template_id', '=', self.milestone_template_id.id), ('id', '!=', self.id)], count=True) > 0:
                raise e.ValidationError('Milestone can be only once in template.')

