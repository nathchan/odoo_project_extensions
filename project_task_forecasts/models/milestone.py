# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectMilestone(models.Model):
    _name = 'project.milestone'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    active = fields.Boolean('Active', default=True, track_visibility='onchange')
    sequence = fields.Integer('Sequence', track_visibility='onchange')
    name = fields.Char('Name', required=True, track_visibility='onchange')
    duration = fields.Integer('Duration', required=True, default=0, track_visibility='onchange')
    predecessor_milestone_id = fields.Many2one('project.milestone', 'Predecessor', track_visibility='onchange')
    predecessor_milestone_ids = fields.Many2many('project.milestone', 'milestone_predecessor_rel', 'current_milestone_id', 'predecessor_milestone_id', 'Predecessors')
    project_id = fields.Many2one('project.project', 'Project', track_visibility='onchange', required=True)
    info = fields.Html('Decription')

    _sql_constraints = [
        ('unique_project_milestone', 'unique(name, project_id)', 'Combination of project and milestone name must be unique!')
    ]