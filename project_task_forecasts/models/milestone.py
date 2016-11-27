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
    project_id = fields.Many2one('project.project', 'Project', track_visibility='onchange')
    info = fields.Html('Decription')
