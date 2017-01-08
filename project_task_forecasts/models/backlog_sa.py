# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools, exceptions as e


class ProjectBacklogSa(models.Model):
    _name = 'project.backlog.sa'
    _auto = False
    _project_name = 'Sprint SA'
    _inherit = ['project.base.backlog']
