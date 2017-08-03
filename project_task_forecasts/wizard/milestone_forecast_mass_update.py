# -*- coding: utf-8 -*-


from openerp import models, fields, api, tools, exceptions as e
import datetime


class MilestoneForecastMassUpdateWizard(models.TransientModel):
    _name = 'project.task.milestone.forecast.mass.update.wizard'

    target_project_id = fields.Many2one('project.project', 'Project')
    target_milestone_id = fields.Many2one('project.milestone', 'Milestone')

    milestone_forecast_ids = fields.Many2many('project.task.milestone.forecast', relation='project_mass_update_wizard_task_milestone_forecast_rel',
                                              string='Targets')

    forecast_date = fields.Date('Forecast date')
    actual_date = fields.Date('Actual date')
    state = fields.Selection([('choose', 'Choose'), ('get', 'Get')], 'State', default='choose')
    updated_count = fields.Integer('Updated tasks count')

    @api.multi
    def apply_dates(self):
        self.ensure_one()

        if not self.forecast_date and not self.actual_date:
            return

        new_vals = {}
        date_seven_days_ago = (datetime.datetime.now() - datetime.timedelta(days=7))
        if self.forecast_date:
            new_vals['forecast_date'] = self.forecast_date
            if datetime.datetime.strptime(new_vals['actual_date'], tools.DEFAULT_SERVER_DATE_FORMAT) <= date_seven_days_ago:
                raise e.ValidationError('Forecast date can not be older than 7 days.')
        if self.actual_date:
            new_vals['actual_date'] = self.actual_date
            if datetime.datetime.strptime(new_vals['actual_date'], tools.DEFAULT_SERVER_DATE_FORMAT) > datetime.datetime.now():
                raise e.ValidationError('Actual date can not be date in future.')
            if datetime.datetime.strptime(new_vals['actual_date'], tools.DEFAULT_SERVER_DATE_FORMAT) <= date_seven_days_ago:
                raise e.ValidationError('Actual date can not be older than 7 days.')

        if self.milestone_forecast_ids and len(self.milestone_forecast_ids) > 0:
            for item in self.milestone_forecast_ids.filtered(lambda x: x.project_id.id == self.target_project_id.id and x.milestone_id.id == self.target_milestone_id.id):
                new_vals['skip_milestones_recalculation'] = True
                item.write(new_vals)
                item.calculate_forecast()

        return True
