# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools, exceptions as e
import datetime


class ProjectBacklogCw(models.AbstractModel):
    _name = 'project.base.backlog'
    _rec_name = 'task_id'
    _order = 'sequence_order'
    _project_name = ''

    @api.multi
    def _compute_color(self):
        for rec in self:
            rec.color = rec.task_id.color
            rec.task_blocked = True if rec.task_id.kanban_state == 'blocked' else False

    create_uid = fields.Many2one('res.users', 'Created by', readonly=True)
    create_date = fields.Datetime('Created date', readonly=True)
    write_uid = fields.Many2one('res.users', 'Updated by', readonly=True)
    write_date = fields.Datetime('Updated date', readonly=True)
    milestone_id = fields.Many2one('project.milestone', 'Milestone', readonly=True)
    project_id = fields.Many2one('project.project', 'Project', readonly=True)
    task_id = fields.Many2one('project.task', 'Task', readonly=True)
    task_active = fields.Boolean('Task Active', readonly=True)
    task_group_id = fields.Many2one('project.task.group', 'Rollout group', readonly=True)
    subcontractor_id = fields.Many2one('res.partner', 'Subcontractor', readonly=True)
    user_id = fields.Many2one('res.users', 'Assigned to', readonly=True)
    forecast_date = fields.Date('Forecast date', readonly=True)
    forecast_week = fields.Char('Forecast week', readonly=True)
    sequence_order = fields.Integer('Sequence', readonly=True)
    task_blocked = fields.Boolean('Task blocked', compute=_compute_color)
    color = fields.Char('Color Index', compute=_compute_color)


    filter_A_B_ordered_on = fields.Date(string='A+B Ordered on', related='task_id.filter_A_B_ordered_on')
    filter_C_ordered_on = fields.Date(string='C Ordered on', related='task_id.filter_C_ordered_on')
    filter_STEEL_ordered_on = fields.Date(string='STEEL Ordered on', related='task_id.filter_STEEL_ordered_on')
    filter_CRANE_ordered_on = fields.Date(string='CRANE Ordered on', related='task_id.filter_CRANE_ordered_on')

    filter_A_B_inbound = fields.Date(string='A+B IRIS inbound', related='task_id.filter_A_B_inbound')
    filter_C_inbound = fields.Date(string='C IRIS inbound', related='task_id.filter_C_inbound')
    filter_STEEL_inbound = fields.Date(string='STEEL IRIS inbound', related='task_id.filter_STEEL_inbound')
    filter_CRANE_inbound = fields.Date(string='CRANE IRIS inbound', related='task_id.filter_CRANE_inbound')

    filter_A_B_outbound = fields.Date(string='A+B IRIS outbound', related='task_id.filter_A_B_outbound')
    filter_C_outbound = fields.Date(string='C IRIS outbound', related='task_id.filter_C_outbound')
    filter_STEEL_outbound = fields.Date(string='STEEL IRIS outbound', related='task_id.filter_STEEL_outbound')
    filter_CRANE_outbound = fields.Date(string='CRANE IRIS outbound', related='task_id.filter_CRANE_outbound')

    @api.multi
    def write(self, vals):
        if len(vals) == 1 and 'kanban_state' in vals:
            for rec in self:
                milestone_forecast = self.env['project.task.milestone.forecast'].search([('task_id', '=', rec.task_id.id),
                                                                                         ('milestone_id', '=', rec.milestone_id.id)],
                                                                                        limit=1)
                milestone_forecast.write({
                    'kanban_state': vals['kanban_state']
                })

        return True

    @api.multi
    def action_show_task_from_milestone(self):
        this = self[0]
        return {
            'type': 'ir.actions.act_window',
            'res_id': this.task_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.task',
            # 'target': 'new',
            # 'context': self.env.context,
        }

    @api.multi
    def set_actual(self):
        this = self[0]
        current_date = datetime.datetime.now().strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
        milestone_forecast = self.env['project.task.milestone.forecast'].search([('task_id', '=', this.task_id.id),
                                                                                 ('milestone_id', '=', this.milestone_id.id)],
                                                                                limit=1)
        milestone_forecast.write({
            'actual_date': current_date
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'kanban,tree',
            'res_model': self._name,
            'context': self.env.context,
        }

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT %s
            FROM ( %s )
            WHERE %s
            ORDER BY %s
            )
        """ % (self._table, self._select(), self._from(), self._where(), self._order_by()))

    def _select(self):
        select_str = """
            (ROW_NUMBER() OVER (ORDER BY f.create_date)) as id,
            f.create_date,
            f.create_uid,
            f.write_date,
            f.write_uid,
            f.milestone_id,
            f.project_id,
            f.task_id,
            t.active as task_active,
            t.user_id,
            t.task_group_id,
            t.subcontractor_id,
            f.forecast_date,
            f.forecast_week,
            f.sequence_order
        """
        return select_str

    def _from(self):
        from_str = """
            project_task_milestone_forecast f
            left join project_project p on p.id = f.project_id
            left join account_analytic_account a on a.id = p.analytic_account_id
            left join project_task t on t.id = f.task_id
        """
        return from_str

    def _where(self):
        where_str = """
                a.name = '%s' and
                f.actual_date is null and
                f.milestone_id in (
                    select
                        distinct mp.current_milestone_id
                    from
                        milestone_predecessor_rel mp
                    where
                        mp.predecessor_milestone_id in (
                            select
                                f1.milestone_id
                            from
                                project_task_milestone_forecast f1
                            where
                                f1.task_id = f.task_id
                                and f1.actual_date is not null
                                and (select count(*) from milestone_predecessor_rel mp1 where mp1.current_milestone_id = f.milestone_id) <= 1
                        )
                    union
                    select
                        distinct mp2.current_milestone_id
                    from
                        milestone_predecessor_rel mp2
                    where
                        (select count(*) from milestone_predecessor_rel mp3 where mp3.current_milestone_id = f.milestone_id)
                        =
                        (select count(*)
                         from project_task_milestone_forecast f2
                         where
                            f2.task_id = f.task_id
                            and f2.actual_date is not null
                            and f2.milestone_id in (
                                select mp4.predecessor_milestone_id
                                from milestone_predecessor_rel mp4
                                where mp4.current_milestone_id = f.milestone_id
                            )
                        )
                )
        """
        return where_str % (self._project_name,)

    def _order_by(self):
        order_str = """
            f.sequence_order
        """
        return order_str
