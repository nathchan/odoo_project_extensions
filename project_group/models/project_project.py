# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    project_group_id = fields.Many2one('project.group', 'Project group')
