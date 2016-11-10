# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools
import openerp.exceptions as e
#from datetime import datetime as d
import datetime as d
import openerp as o

class HrWeekendGenerator(models.TransientModel):
    _name = 'hr.weekend.generator'

    year = fields.Selection([(2016, '2016'),
                             (2017, '2017'),
                             (2018, '2018'),
                             (2019, '2019'),
                             (2020, '2020')], 'Year', required=True)
    state = fields.Selection([('choose', 'Choose'), ('finish', 'Finish')], 'State', default='choose')
    errors = fields.Text('Errors')

    @api.multi
    def generate_weekends(self):
        category_weekend = self.env['hr.day.off.category'].search([('name', '=', 'Weekend')])
        if not category_weekend:
            raise e.UserError('Category "Weekend" does not exist. Please create one and try again.')

        this = self[0]
        current_date = d.datetime(this.year, 1, 1)
        end_date = d.datetime(this.year, 12, 31)
        weekend_number = 0
        error_msg = ''
        while(current_date <= end_date):
            weekday = current_date.weekday()
            if weekday >= 5:  # sunday == 6
                if weekday == 5:
                    weekend_number += 1
                data = {
                    'date': current_date.strftime(tools.DEFAULT_SERVER_DATE_FORMAT),
                    'category_id': category_weekend.id,
                    'info': 'Weekend '+str(this.year)+'-'+str(weekend_number)
                }
                try:
                    self.env['hr.day.off'].create(data)
                except:
                    error_msg += 'Date '+current_date.strftime(tools.DEFAULT_SERVER_DATE_FORMAT)+' already exist.\n'
            current_date += d.timedelta(days=1)

        self.write({
            'state': 'finish',
            'errors': error_msg if error_msg else 'No errors.',
        })
        return {
            'type': 'ir.actions.act_window',
            'res_id': self[0].id,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.weekend.generator',
            'target': 'new',
            'context': self.env.context,
        }