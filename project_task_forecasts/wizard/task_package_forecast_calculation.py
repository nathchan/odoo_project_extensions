# -*- coding: utf-8 -*-


from openerp import models, fields, api, tools, exceptions as e


class TaskPackageForecastCalculationWizard(models.TransientModel):
    _name = 'project.task.package.forecast.calculation.wizard'

    project_id = fields.Many2one('project.project', 'Project')
    task_package_id = fields.Many2one('project.task.package', 'Task package')
    forecast_date = fields.Date('First milestone FC date')
    state = fields.Selection([('choose', 'Choose'), ('get', 'Get')], 'State', default='choose')

    @api.multi
    def do_calculations(self):
        this = self[0]




        self.write({'state': 'get'})

        return {
            'type': 'ir.actions.act_window',
            'res_id': this.id,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.task.package.forecast.calculation.wizard',
            'target': 'new',
            'context': self.env.context,
        }
