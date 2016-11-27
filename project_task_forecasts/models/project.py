# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    milestone_ids = fields.One2many('project.milestone', 'project_id', 'Milestones')
