# -*- coding: utf-8 -*-


from openerp import models, fields, api, tools, exceptions as e


class TaskPackageForecastCalculationWizard(models.TransientModel):
    _name = 'project.task.package.forecast.calculation.wizard'

    project_id = fields.Many2one('project.project', 'Project')
    package_id = fields.Many2one('project.task.package', 'Package')
    forecast_date = fields.Date('First milestone FC date')
    state = fields.Selection([('choose', 'Choose'), ('get', 'Get')], 'State', default='choose')
    updated_count = fields.Integer('Updated tasks count')

    @api.one
    def do_calculations(self):
        this = self

        if not this.project_id or not this.package_id or not this.forecast_date:
            raise e.ValidationError('First select project, package and date.')

        tasks = self.env['project.task'].search([('project_id', '=', this.project_id.id),
                                                 ('task_package_id', '=', this.package_id.id)])

        for task in tasks:
            task.forecast_start_date = this.forecast_date
            task.action_fill_forecast_dates()

        self.write({
            'state': 'get',
            'updated_count': len(tasks),
        })

        return {
            'type': 'ir.actions.act_window',
            'res_id': this.id,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.task.package.forecast.calculation.wizard',
            'target': 'new',
            'context': self.env.context,
        }
