# -*- coding: utf-8 -*-

from openerp import models, fields, api
import datetime


class ProjectTaskPhoneCall(models.Model):
    _name = 'project.task.phone.call'
    _order = 'date DESC'

    task_id = fields.Many2one('project.task', 'Task', required=True)
    date = fields.Date('Date', default=datetime.datetime.today().strftime('%Y-%m-%d'), required=True)
    partner_id = fields.Many2one('res.partner', 'Contact')
    user_id = fields.Many2one('res.users', 'Responsible', required=True)
    info = fields.Text('Call summary')

