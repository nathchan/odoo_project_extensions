# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools, exceptions as e
import datetime


class ProjectBacklogCw(models.Model):
    _name = 'project.backlog.cw'
    _auto = False
    _project_name = 'LTE800'
    _inherit = ['project.base.backlog']
