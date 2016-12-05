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

        # if not this.project_id or not this.package_id or not this.forecast_date:
        #     raise e.ValidationError('First select project, package and date.')

        project_SA = self.env['project.project'].search([('name', '=', 'Sprint SA')], limit=1)
        new_milestone = self.env['project.milestone'].search([('name', '=', '0900')], limit=1)
        tasks = self.env['project.task'].search([('project_id', '=', project_SA.id)])
        for task in tasks:
            data = {
                'task_id': task.id,
                'project_id': task.project_id.id,
                'milestone_id': new_milestone.id,
                'baseline_duration': new_milestone.duration,
                'duration_forecast': new_milestone.duration,
            }
            milestone = self.env['project.task.milestone.forecast'].create(data)



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
