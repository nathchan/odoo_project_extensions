# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools
import datetime

class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    @api.onchange('date_from', 'date_to')
    @api.one
    def calculate_number_of_days(self):
        self.number_of_days_temp = 0
        if self.date_from and self.date_to and self.date_from <= self.date_to:
            current_date = datetime.datetime.strptime(self.date_from, tools.DEFAULT_SERVER_DATE_FORMAT)
            end_date = datetime.datetime.strptime(self.date_to, tools.DEFAULT_SERVER_DATE_FORMAT)
            days_sum = 0
            while current_date <= end_date:
                count = self.env['hr.day.off'].search([('date', '=', current_date.strftime(tools.DEFAULT_SERVER_DATE_FORMAT))], count=True)
                if count == 0:
                    days_sum += 1
                current_date = current_date + datetime.timedelta(days=1)
            self.number_of_days_temp = days_sum

    @api.onchange('holiday_status_id')
    @api.one
    def onchange_holiday_status(self):
        self.name = ''
        if self.holiday_status_id:
            self.name = self.holiday_status_id.name

    @api.depends('number_of_days_temp')
    @api.multi
    def _compute_num_of_days_to_display(self):
        for rec in self:
            rec.number_of_days_to_display = rec.number_of_days_temp

    date_from = fields.Date('Start Date', readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, select=True, copy=False)
    date_to = fields.Date('End Date', readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, copy=False)
    number_of_days_to_display = fields.Integer('Duration to display', compute=_compute_num_of_days_to_display)
