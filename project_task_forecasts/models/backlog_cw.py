# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools


class ProjectBacklogCw(models.Model):
    _name = 'project.backlog.cw'
    _auto = False
    _rec_name = 'task_id'
    _order = 'sequence_order'

    milestone_id = fields.Many2one('project.milestone', 'Milestone', readonly=True)
    project_id = fields.Many2one('project.project', 'Project', readonly=True)
    task_id = fields.Many2one('project.task', 'Task', readonly=True)
    user_id = fields.Many2one('res.users', 'Assigned to', readonly=True)
    forecast_date = fields.Date('Forecast date', readonly=True)
    forecast_week = fields.Char('Forecast week', readonly=True)
    sequence_order = fields.Integer('Sequence', readonly=True)

    def _select(self):
        select_str = """
            (ROW_NUMBER() OVER (ORDER BY f.create_date)) as id,
            f.milestone_id,
            f.project_id,
            f.task_id,
            t.user_id,
            f.forecast_date,
            f.forecast_week,
            f.sequence_order,
            f.write_date,
            f.write_uid
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
                a.name = 'LTE800' and
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
        return where_str

    def _order_by(self):
        order_str = """
            f.sequence_order
        """
        return order_str

    def init(self, cr):
        # self._table = sale_report
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT %s
            FROM ( %s )
            WHERE %s
            ORDER BY %s
            )
        """ % (self._table, self._select(), self._from(), self._where(), self._order_by()))
