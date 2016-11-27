# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    milestone_id = fields.Many2one('project.task.type', 'Milestone')
