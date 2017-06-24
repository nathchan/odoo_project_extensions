# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools, exceptions as e


class ProjectBacklogSran(models.Model):
    _name = 'project.backlog.sran'
    _auto = False
    _project_name = 'SRAN'
    _inherit = ['project.base.backlog']
