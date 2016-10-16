# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import Warning
import datetime


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.multi
    def _compute_milestone_count(self):
        for obj in self:
            obj.milestone_count = len(obj.milestone_ids)

    @api.multi
    @api.depends('milestone_ids.actual_date')
    def _compute_stage_progress(self):
        for obj in self:
            actuals = self.env['project.task.stage.forecast'].search_count([('task_id', '=', obj.id),
                                                                            ('actual_date', '!=', None)])
            total = obj.milestone_count
            if not total or total == 0:
                obj.stage_progress = 0
            else:
                obj.stage_progress = float(float(actuals) / float(total)) * 100.0

    @api.one
    def _compute_has_processes(self):
        proc_count = len(self.stage_id.process_ids)
        if proc_count > 1:
            self.has_processes = True

        else:
            self.has_processes = False

    forecast_project_id = fields.Many2one('project.project', 'Forecast project')
    forecast_start_date = fields.Date('Forecast start date')

    milestone_ids = fields.One2many('project.task.stage.forecast', 'task_id', 'Stages forecast')
    milestone_count = fields.Integer('Milestone count', compute=_compute_milestone_count)
    stage_progress = fields.Float('Percent complete', compute=_compute_stage_progress, store=True, group_operator="avg")
    subcontractor_id = fields.Many2one('res.partner', 'Subcontractor')
    work_package = fields.Char('Work Package ID')

    has_processes = fields.Boolean('Has processes', compute=_compute_has_processes)
    stage_process_id = fields.Many2one('project.task.stage.process', 'Process')

    @api.multi
    def write(self, vals):
        if 'stage_id' in vals:
            stage_id = vals.get('stage_id')
            process_id = self.env['project.task.stage.process'].search([('stage_id', '=', stage_id)],
                                                                                          limit=1)
            vals.update({'stage_process_id': process_id.id})
        return super(ProjectTask, self).write(vals)

    def copy(self, cr, uid, id, default=None, context=None):
        new_id = super(ProjectTask, self).copy(cr, uid, id, default, context)
        forecast_tbl = self.pool.get('project.task.stage.forecast')
        task_obj = self.pool.get('project.task').browse(cr, uid, new_id)
        for stage in task_obj.project_id.type_ids:
            data = {
                'task_id': task_obj.id,
                'project_id': task_obj.project_id.id,
                'stage_id': stage.id,
                'sequence': task_obj.sequence
            }
            forecast_tbl.create(cr, uid, data, context)
        return new_id

    @api.one
    def action_fill_forecast_dates(self):
        if not (self.forecast_project_id and self.forecast_start_date):
            raise Warning('Please first enter project and start date.')


        lines = None
        forecast_ref = self.env['project.task.stage.forecast']
        records_existing = forecast_ref.search([('task_id', '=', self.id),
                                                ('project_id', '=', self.forecast_project_id.id)],
                                               order='sequence')

        if records_existing and len(records_existing) > 0:
            lines = records_existing
        else:
            stages = self.forecast_project_id.type_ids
            for stage in stages:
                forecast_ref.sudo().create({
                    'project_id': self.forecast_project_id.id,
                    'task_id': self.id,
                    'stage_id': stage.id,
                })
            lines = forecast_ref.search([('task_id', '=', self.id), ('project_id', '=', self.forecast_project_id.id)],
                                        order='sequence')
        start_date = datetime.datetime.strptime(self.forecast_start_date, '%Y-%m-%d')
        for line in lines:
            business_days_to_add = line.duration_forecast
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

    def return_action_to_open_milestones(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        obj = self.pool.get('project.task').browse(cr, uid, ids[0], context)
        res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'project_task_forecasts', 'view_task_milestones_show_action', context=context)
        res['context'] = context
        res['context'].update({'default_task_id': ids[0], 'default_project_id': obj.project_id.id})
        res['context'].update({'order_by': 'sequence'})
        res['context'].update({'group_by': 'project_id'})
        res['domain'] = [('task_id', '=', ids[0])]
        return res
