# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectMilestone(models.Model):
    _name = 'project.milestone'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'sequence_order'

    @api.multi
    def _compute_str_predecessors(self):
        for rec in self:
            if len(rec.predecessor_milestone_ids) > 0:
                rec.str_predecessor_milestone_ids = ', '.join([item.name for item in rec.predecessor_milestone_ids])
            else:
                rec.str_predecessor_milestone_ids = ''

    active = fields.Boolean('Active', default=True, track_visibility='onchange')

    sequence_order = fields.Integer('Default sequence', track_visibility='onchange')
    name = fields.Char('Name', required=True, track_visibility='onchange')
    duration = fields.Integer('Default duration', required=True, default=0, track_visibility='onchange')
    str_predecessor_milestone_ids = fields.Char('Default predecessors', compute=_compute_str_predecessors)

    predecessor_milestone_ids = fields.Many2many('project.milestone', 'milestone_predecessor_rel', 'current_milestone_id', 'predecessor_milestone_id', 'Predecessors')
    project_id = fields.Many2one('project.project', 'Project', track_visibility='onchange', required=True)
    info = fields.Html('Decription')
    show_on_dispatching = fields.Boolean('Show on dispatching?')
    export_task_wp_code = fields.Selection([('sa', 'SA'),
                                            ('cw', 'CW'),
                                            ('ti', 'TI')], string='Work Package for export')

    #old fields
    sequence = fields.Integer('Sequence', track_visibility='onchange') #old field
    predecessor_milestone_id = fields.Many2one('project.milestone', 'Predecessor', track_visibility='onchange')

    _sql_constraints = [
        ('unique_project_milestone', 'unique(name, project_id)', 'Combination of project and milestone name must be unique!')
    ]

    @api.one
    def add_in_tasks(self):
        self.ensure_one()

        query = """
            select distinct
                task_id
            from
                project_task_milestone_forecast
            where
                project_id = %s
        """
        self.env.cr.execute(query % (self.project_id.id))
        res = self.env.cr.dictfetchall()
        task_ids = [item['task_id'] for item in res]

        for task_id in task_ids:
            self.env['project.task.milestone.forecast'].create({
                'project_id': self.project_id.id,
                'task_id': task_id,
                'milestone_id': self.id,
                'baseline_duration': self.duration,
                'duration_forecast': self.duration,
            })