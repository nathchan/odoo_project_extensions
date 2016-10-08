# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectStage(models.Model):
    _inherit = 'project.task.type'

    is_priority_one = fields.Boolean('Is priority one')
