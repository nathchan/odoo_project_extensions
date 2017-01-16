# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectTaskMilestoneUpdateLog(models.Model):
    _name = 'project.task.milestone.update.log'

    timestamp = fields.Datetime('Timestamp')
    milestone_line_id = fields.Many2one('project.task.milestone.forecast', 'Milestone line')
    updated_field = fields.Selection([('forecast', 'Forecast'), ('actual', 'Actual')], 'Updated field')
