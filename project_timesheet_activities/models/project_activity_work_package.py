# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectActivityWorkPackage(models.Model):
    _name = 'project.activity.work.package'

    name = fields.Char('Name', required=True)
    info = fields.Text('Description')
    sap_report_task_sufix = fields.Char('Task sufix')
    sap_report_service_number = fields.Char('Service number')
