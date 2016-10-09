# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectStage(models.Model):
    _inherit = 'project.task.type'

    quick_view = fields.Boolean('Quick view', default=False)
