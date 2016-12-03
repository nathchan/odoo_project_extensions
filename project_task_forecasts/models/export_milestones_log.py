# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectExportMilestonesLog(models.Model):
    _name = 'project.export.milestones.log'

    timestamp = fields.Datetime('Timestamp')
    project_id = fields.Many2one('project.project', 'Project')
