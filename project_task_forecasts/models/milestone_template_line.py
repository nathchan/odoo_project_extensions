# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions as ex


class MilestoneTemplateLine(models.Model):
    _inherit = 'project.milestone.template.line'

    milestone_template_id = fields.Many2one('project.milestone.template', 'Template')
    milestone_id = fields.Many2one('project.milestone')
