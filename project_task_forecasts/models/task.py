# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools, exceptions as e
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
            actuals = self.env['project.task.milestone.forecast'].search_count([('task_id', '=', obj.id),
                                                                            ('actual_date', '!=', None)])
            total = obj.milestone_count
            if not total or total == 0:
                obj.stage_progress = 0
            else:
                obj.stage_progress = float(float(actuals) / float(total)) * 100.0

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
    forecast_project_id = fields.Many2one('project.project')

    milestone_template_id = fields.Many2one('project.milestone.template', 'Milestones template')

    milestone_ids = fields.One2many('project.task.milestone.forecast', 'task_id', 'Milestones forecast')
    milestone_count = fields.Integer('Milestone count', compute=_compute_milestone_count)
    stage_progress = fields.Float('Percent complete', compute=_compute_stage_progress, store=True, group_operator="avg")
    subcontractor_id = fields.Many2one('res.partner', 'Subcontractor')
    work_package = fields.Char('Work Package ID')
    priority_id = fields.Many2one('project.task.priority', 'MDF Priority')
    quality_finish = fields.Boolean('Quality Finish')

    blocked_until = fields.Date('Blocked until')

    @api.multi
    def apply_milestone_template(self):
        for task in self:
            if not task.milestone_template_id:
                continue

            template = task.milestone_template_id

            #milestones that are in old and new template
            mutual_milestones = self.env['project.task.milestone.forecast'].search([('task_id', '=', task.id),
                                                                                    ('milestone_id', 'in', [item.milestone_id.id for item in template.line_ids])])
            for ms in mutual_milestones:
                new_duration = template.line_ids.filtered(lambda x: x.milestone_id.id == ms.milestone_id.id).duration
                new_sequence_order = template.line_ids.filtered(lambda x: x.milestone_id.id == ms.milestone_id.id).sequence_order
                ms.write({
                    'duration_forecast': new_duration,
                    'baseline_duration': new_duration,
                    'sequence_order': new_sequence_order,
                    'force_update': True,
                })

            # milestones in old template, but don't exist in new
            old_milestones = self.env['project.task.milestone.forecast'].search([('task_id', '=', task.id),
                                                                                 ('milestone_id', 'not in', [item.milestone_id.id for item in template.line_ids])])
            for ms in old_milestones:
                ms.active = False

            # milestones not in old template, but exist in new (should be activated or created)
            new_milestones = self.env['project.milestone.template.line'].search([('milestone_template_id', '=', template.id),
                                                                                 ('milestone_id', 'not in', [item.milestone_id.id for item in task.milestone_ids])])
            for ms in new_milestones:
                archived = self.env['project.task.milestone.forecast'].search([('task_id', '=', task.id),
                                                                               ('milestone_id', '=', ms.milestone_id.id),
                                                                               ('active', '=', False)], limit=1)
                if archived:
                    # unarchive
                    archived.write({
                        'active': True,
                        'duration_forecast': ms.duration,
                        'baseline_duration': ms.duration,
                        'sequence_order': ms.sequence_order,
                        'force_update': True,
                    })
                else:
                    # create new
                    self.env['project.task.milestone.forecast'].create({
                        'task_id': task.id,
                        'project_id': template.project_id.id,
                        'milestone_id': ms.milestone_id.id,
                        'baseline_duration': ms.duration,
                        'duration_forecast': ms.duration,
                        'sequence_order': ms.sequence_order,
                    })


            # recalculate new dates
            first_ms = self.env['project.task.milestone.forecast'].search([('task_id', '=', task.id)], order='sequence_order', limit=1)
            if first_ms.forecast_date or first_ms.actual_date:
                first_ms.calculate_forecast()

    @api.multi
    def write(self, vals):
        updated_task = super(ProjectTask, self).write(vals)

        if 'milestone_template_id' in vals and vals['milestone_template_id'] is not False:
            err_msgs = []
            try:
                updated_task.apply_milestone_template()
            except Exception as e:
                err_msgs.append(e.name)

            if len(err_msgs) > 0:
                raise e.UserError('\n\n\n'.join(err_msgs))

        return updated_task

    @api.model
    def create(self, vals):
        new_task = super(ProjectTask, self).create(vals)
        default_template = self.env['project.milestone.template'].search([('project_id', '=', new_task.project_id.id),
                                                                          ('is_default', '=', True)],
                                                                         limit=1)
        if default_template:
            forecast_tbl = self.env['project.task.milestone.forecast']
            for line in default_template.line_ids:
                data = {
                    'task_id': new_task.id,
                    'project_id': new_task.project_id.id,
                    'milestone_id': line.milestone_id.id,
                    'baseline_duration': line.duration,
                    'duration_forecast': line.duration,
                    'sequence_order': line.sequence_order,
                }
                forecast_tbl.create(data)
        return new_task

    def copy(self, cr, uid, id, default=None, context=None):
        new_id = super(ProjectTask, self).copy(cr, uid, id, default, context)
        new_task = self.pool.get('project.task').browse(cr, uid, new_id)

        default_template = self.env['project.milestone.template'].search([('project_id', '=', new_task.project_id.id),
                                                                          ('is_default', '=', True)],
                                                                         limit=1)

        if default_template:
            forecast_tbl = self.env['project.task.milestone.forecast']
            for line in default_template.line_ids:
                data = {
                    'task_id': new_task.id,
                    'project_id': new_task.project_id.id,
                    'milestone_id': line.milestone_id.id,
                    'baseline_duration': line.duration,
                    'duration_forecast': line.duration,
                    'sequence_order': line.sequence_order,
                }
                forecast_tbl.create(data)
        return new_id

    @api.one
    def action_fill_milestones(self):
        forecast_ref = self.env['project.task.milestone.forecast']
        records_existing = forecast_ref.search([('task_id', '=', self.id),
                                                ('project_id', '=', self.project_id.id)],
                                               order='sequence_order')

        if records_existing and len(records_existing) > 0:
            return

        default_template = self.env['project.milestone.template'].search([('project_id', '=', self.project_id.id),
                                                                          ('is_default', '=', True)],
                                                                         limit=1)
        if not default_template:
            raise Warning('Project does not have default milestones template.')

        if default_template:
            forecast_tbl = self.env['project.task.milestone.forecast']
            for line in default_template.line_ids:
                data = {
                    'task_id': self.id,
                    'project_id': self.project_id.id,
                    'milestone_id': line.milestone_id.id,
                    'baseline_duration': line.duration,
                    'duration_forecast': line.duration,
                    'sequence_order': line.sequence_order,
                }
                forecast_tbl.create(data)

        return

    def return_action_to_open_milestones(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        obj = self.pool.get('project.task').browse(cr, uid, ids[0], context)
        res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'project_task_forecasts', 'view_task_milestones_show_action', context=context)
        res['context'] = context
        res['context'].update({'default_task_id': ids[0], 'default_project_id': obj.project_id.id})
        res['context'].update({'order_by': 'sequence_order'})
        res['domain'] = [('task_id', '=', ids[0])]
        return res
