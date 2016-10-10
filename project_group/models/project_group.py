# -*- coding: utf-8 -*-

from openerp import models, fields, api
import datetime


class ProjectGroup(models.Model):
    _name = 'project.group'

    name = fields.Char('Name', required=True)
    info = fields.Text('Description')
    project_ids = fields.One2many('project.project', 'project_group_id', 'Projects', readonly=True)


class ProjectProject(models.Model):
    _inherit = 'project.project'

    project_group_id = fields.Many2one('project.group')

