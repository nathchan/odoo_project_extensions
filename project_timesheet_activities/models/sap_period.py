# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools, exceptions as e
import datetime

class SapPeriod(models.Model):
    _name = 'hr.timesheet.sap.period'
    _rec_name = 'period_name'
    _order = 'period_to DESC'

    @api.multi
    def _compute_period_name(self):
        for rec in self:
            from_date = datetime.datetime.strptime(rec.period_from, tools.DEFAULT_SERVER_DATE_FORMAT)
            to_date = datetime.datetime.strptime(rec.period_to, tools.DEFAULT_SERVER_DATE_FORMAT)
            rec.period_name = from_date.strftime('%d.%m.%Y') + ' - ' + to_date.strftime('%d.%m.%Y')

    period_name = fields.Char('Display name', compute=_compute_period_name)
    is_locked = fields.Boolean('Is locked', default=False)
    period_from = fields.Date('Period from', required=True)
    period_to = fields.Date('Period to', required=True)
    last_post = fields.Datetime('Last post')
    remarks = fields.Text('Remarks')

    @api.constrains('period_from', 'period_to')
    def sap_dates_constrains(self):
        if self.period_from and self.period_to and self.period_to < self.period_from:
            raise e.ValidationError('Period from must be before period to.')
