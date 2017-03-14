# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools
from openerp import exceptions as e



class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.multi
    def _compute_on_site_activity_without_dispatching(self):
        for rec in self:
            rec.on_site_activity_without_dispatching = False
            if rec.timesheet_approved_status not in ['refused', 'approved'] and rec.account_id and rec.task_id:
                query = """
                    select
                        count(*)
                    from
                        project_dispatching disp
                    where
                        disp.task_id = %s
                        and datetime_start::DATE <= '%s'
                        and datetime_stop::DATE >= '%s'
                """
                self.env.cr.execute(query % (rec.task_id.id, rec.date, rec.date))
                count = self.env.cr.fetchone()[0]
                if count < 1:
                    rec.on_site_activity_without_dispatching = True

    def _search_on_site_activity_without_dispatching(self, operator, value):
        if (operator == '=' and value is True) or (operator == '!=' and value is False):
            new_operator = 'in'
        else:
            new_operator = 'not in'

        db_list = []
        query = """
            select
                line.id
            from
                account_analytic_line line
                left join project_dispatching disp on
                    (disp.task_id = line.task_id
                     and disp.datetime_start::DATE <= line.date
                     and disp.datetime_stop::DATE >= line.date)
            where
                line.timesheet_approved_status not in ('approved', 'refused')
                and line.account_id is not null
                and line.task_id is not null
                and disp.id is null
        """
        self.env.cr.execute(query)
        db_list = self.env.cr.fetchall()
        res_ids = []
        for item in db_list:
            res_ids.append(item[0])
        return [('id', new_operator, res_ids)]

    on_site_activity_without_dispatching = fields.Boolean('On site activity without dispatching', compute=_compute_on_site_activity_without_dispatching, search=_search_on_site_activity_without_dispatching)
