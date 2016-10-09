# -*- coding: utf-8 -*-

from openerp import models, fields, api
import datetime


class ProjectTask(models.Model):
    _inherit = 'project.task'

    forecast_start_date = fields.Date('Forecast start date')
    forecast_ids = fields.One2many('project.task.stage.forecast', 'task_id', 'Stages forecast')
    stage_progress = fields.Float('Stage progress', readonly=True)
    subcontractor_id = fields.Many2one('res.partner', 'Subcontractor')
    work_package = fields.Char('Work Package ID')

    def copy(self, cr, uid, id, default=None, context=None):
        new_id = super(ProjectTask, self).copy(cr, uid, id, default, context)
        forecast_tbl = self.pool.get('project.task.stage.forecast')
        task_obj = self.pool.get('project.task').browse(cr, uid, new_id)
        for stage in task_obj.project_id.type_ids:
            data = {
                'task_id': task_obj.id,
                'project_id': task_obj.project_id.id,
                'stage_id': stage.id,
            }
            forecast_tbl.create(cr, uid, data, context)
        return new_id

    @api.one
    def action_fill_forecast_dates(self):
        line_ids = self.forecast_ids
        start_date = datetime.datetime.strptime(self.forecast_start_date, '%Y-%m-%d')
        for line in line_ids:
            business_days_to_add = line.stage_id.duration_forecast
            current_date = start_date
            while business_days_to_add > 0:
                current_date += datetime.timedelta(days=1)
                weekday = current_date.weekday()
                if weekday >= 5: # sunday = 6
                    continue
                business_days_to_add -= 1
            line.forecast_date = current_date.strftime('%Y-%m-%d')
            start_date = current_date
        return True


        # if self.forecast_date:
        #     task_id = self.task_id.id
        #     records = self.search([('task_id', '=', task_id), ('sequence', '>', self.sequence)],
        #                           order='sequence')
        #     if records:
        #         start_date = self.forecast_date
        #         for rec in records:
        #             # business_days_to_add = rec.stage_id.duration_forecast
        #             # current_date = start_date
        #             # while business_days_to_add > 0:
        #             #     current_date += datetime.timedelta(days=1)
        #             #     weekday = current_date.weekday()
        #             #     if weekday >= 5: # sunday = 6
        #             #         continue
        #             #     business_days_to_add -= 1
        #             # rec.forecast_date = current_date
        #             rec.forecast_date = start_date



class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    duration_forecast = fields.Integer('Duration forecast')

class ProjectTaskStagesForecast(models.Model):
    _name = 'project.task.stage.forecast'

    project_id = fields.Many2one('project.project', 'Project', related='task_id.project_id')
    task_id = fields.Many2one('project.task', 'Task', required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence', related='stage_id.sequence', store=True)
    stage_id = fields.Many2one('project.task.type', 'Stage', domain="[('project_ids', '=', project_id)])",
                               required=True, ondelete='cascade')
    forecast_date = fields.Date('Forecast date')
    actual_date = fields.Date('Actual date')
