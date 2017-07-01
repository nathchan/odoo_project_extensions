# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools, exceptions as e
import datetime

class HrHolidaysStatus(models.Model):
    _inherit = 'hr.holidays.status'

    timesheet_start_time = fields.Float('Timesheet Start Time')
    timesheet_end_time = fields.Float('Timesheet End Time')

    @api.one
    @api.constrains('timesheet_start_time', 'timesheet_end_time')
    def _check_start_end_time(self):
        if (self.timesheet_start_time != 0) and (self.timesheet_end_time != 0):
            if self.timesheet_start_time >= self.timesheet_end_time:
                raise e.ValidationError('Start time must be before end time.')
            if (self.timesheet_start_time < 0) or (self.timesheet_end_time < 0):
                raise e.ValidationError('Start and end time must be non negative.')
            if (self.timesheet_start_time >= 24) or (self.timesheet_end_time >= 24):
                raise e.ValidationError('Time value must be between 00:00 and 23:59')