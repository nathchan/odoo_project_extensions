# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

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


class ProjectTaskStagesForecast(models.Model):
    _name = 'project.task.stage.forecast'

    project_id = fields.Many2one('project.project', 'Project', related='task_id.project_id')
    task_id = fields.Many2one('project.task', 'Task')
    sequence = fields.Integer('Sequence', related='stage_id.sequence')
    stage_id = fields.Many2one('project.task.type', 'Stage', domain="[('project_ids', '=', project_id)])",
                               required=True)
    forecast_date = fields.Date('Forecast date')
    actual_date = fields.Date('Actual date')

