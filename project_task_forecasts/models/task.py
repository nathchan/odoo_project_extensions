# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import Warning, ValidationError
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

    @api.multi
    def _compute_color(self):
        for rec in self:
            missing_goods_category = self.env['project.issue.category'].search([('name', '=', 'Missing Goods')])
            missing_goods_A = self.env['project.issue.subcategory'].search([('name', '=', 'A Goods')])
            missing_goods_B = self.env['project.issue.subcategory'].search([('name', '=', 'B Goods')])
            missing_goods_C = self.env['project.issue.subcategory'].search([('name', '=', 'C Goods')])
            missing_goods_A_B_issues_count = self.env['project.issue'].search([('task_id', '=', rec.id),
                                                                               ('active', '=', True),
                                                                               ('category_id', '=', missing_goods_category.id),
                                                                               '|',
                                                                               ('subcategory_id', '=', missing_goods_A.id),
                                                                               ('subcategory_id', '=', missing_goods_B.id)],
                                                                              count=True)
            missing_goods_C_issues_count = self.env['project.issue'].search([('task_id', '=', rec.id),
                                                                             ('active', '=', True),
                                                                             ('category_id', '=', missing_goods_category.id),
                                                                             ('subcategory_id', '=', missing_goods_C.id)],
                                                                            count=True)

            if missing_goods_A_B_issues_count > 0:
                rec.color = '3'
            elif missing_goods_C_issues_count > 0:
                rec.color = '4'

    color = fields.Char('Color Index', compute=_compute_color)

    forecast_start_date = fields.Date('Forecast start date')

    milestone_ids = fields.One2many('project.task.milestone.forecast', 'task_id', 'Milestones forecast')
    milestone_count = fields.Integer('Milestone count', compute=_compute_milestone_count)
    stage_progress = fields.Float('Percent complete', compute=_compute_stage_progress, store=True, group_operator="avg")
    subcontractor_id = fields.Many2one('res.partner', 'Subcontractor')
    work_package = fields.Char('Work Package ID')

    has_processes = fields.Boolean('Has processes', compute=_compute_has_processes)
    stage_process_id = fields.Many2one('project.task.stage.process', 'Process')

    @api.multi
    def write(self, vals):
        if 'stage_id' in vals:
            stage_1100_1200 = self.env['project.task.type'].search([('name', '=', '1100-1200')], limit=1)
            new_stage = self.env['project.task.type'].search([('id', '=', vals['stage_id'])], limit=1)
            if stage_1100_1200 and new_stage and self.stage_id.id == stage_1100_1200.id:
                if new_stage.sequence > stage_1100_1200.sequence:
                    # provjeriti da li ima missing goods otvorenih issues
                    missing_goods_category = self.env['project.issue.category'].search([('name', '=', 'Missing Goods')])
                    missing_goods_issues_count = self.env['project.issue'].search([('task_id', '=', self.id),
                                                                                   ('active', '=', True),
                                                                                   ('category_id', '=', missing_goods_category.id)], count=True)
                    if missing_goods_issues_count > 0:
                        raise ValidationError('Issues with Category "Missing Goods" are still opened. Close these Issues First.')

        if 'stage_id' in vals:
            stage_id = vals.get('stage_id')
            process_id = self.env['project.task.stage.process'].search([('stage_id', '=', stage_id)],
                                                                                          limit=1)
            vals.update({'stage_process_id': process_id.id})
        return super(ProjectTask, self).write(vals)

    def copy(self, cr, uid, id, default=None, context=None):
        new_id = super(ProjectTask, self).copy(cr, uid, id, default, context)
        forecast_tbl = self.pool.get('project.task.milestone.forecast')
        task_obj = self.pool.get('project.task').browse(cr, uid, new_id)
        for milestone in task_obj.project_id.milestone_ids:
            data = {
                'task_id': task_obj.id,
                'project_id': task_obj.project_id.id,
                'milestone_id': milestone.id,
            }
            forecast_tbl.create(cr, uid, data, context)
        return new_id

    @api.one
    def action_fill_forecast_dates(self):
        pass
        if not self.forecast_start_date:
            raise Warning('First enter forecast start date, please.')


        lines = None
        forecast_ref = self.env['project.task.milestone.forecast']
        records_existing = forecast_ref.search([('task_id', '=', self.id),
                                                ('project_id', '=', self.project_id.id)],
                                               order='sequence')

        if records_existing and len(records_existing) > 0:
            lines = records_existing
        else:
            milestones = self.project_id.milestone_ids
            for milestone in milestones:
                forecast_ref.sudo().create({
                    'project_id': self.forecast_project_id.id,
                    'task_id': self.id,
                    'milestone_id': milestone.id,
                })
            lines = forecast_ref.search([('task_id', '=', self.id), ('project_id', '=', self.project_id.id)],
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
