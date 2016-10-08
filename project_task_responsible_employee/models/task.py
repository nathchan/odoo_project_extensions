# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    responsible_employee_id = fields.Many2one('hr.employee', 'Responsible employee')
