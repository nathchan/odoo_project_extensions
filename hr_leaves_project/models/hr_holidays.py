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
            current_date = datetime.datetime.strptime(self.date_from, tools.DEFAULT_SERVER_DATETIME_FORMAT)
            end_date = datetime.datetime.strptime(self.date_to, tools.DEFAULT_SERVER_DATETIME_FORMAT)
            days_sum = 0
            while current_date <= end_date:
                count = self.env['hr.day.off'].search([('date', '=', current_date.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT))], count=True)
                if count == 0:
                    days_sum += 1
                current_date = current_date + datetime.timedelta(days=1)
            self.number_of_days_temp = days_sum
