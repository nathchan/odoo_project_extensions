# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    task_group_id = fields.Many2one('project.task.group', 'Rollout group')
