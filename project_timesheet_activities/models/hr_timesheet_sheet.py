# -*- coding: utf-8 -*-

from openerp import models, fields, api

class HrTimesheetSheet(models.Model):
    _inherit = 'hr_timesheet_sheet.sheet'

    @api.multi
    def _compute_no_break_working_hours_warning(self):
        for rec in self:
            db = self.env.cr
            break_query = """
                select
                (
                    select
                        count(*)
                    from
                    (
                        select
                            count(*)
                        from
                            account_analytic_line l
                        where
                            l.sheet_id = %d
                        group by
                            sheet_id, date
                        having
                            sum(unit_amount) >= 8.0
                            and sum(timesheet_break_amount) < 0.5
                    ) as tbl
                ) as break_warning,
                (
                    select
                        count(*)
                    from
                    (
                        select
                            count(*)
                        from
                            account_analytic_line l
                        where
                            l.sheet_id = %d
                        group by
                            sheet_id, date
                        having
                            sum(unit_amount) > 10.0
                    ) as tbl
                ) as working_hours_warning
            """
            db.execute(break_query % (rec.id, rec.id,))
            counts = db.fetchone()
            rec.no_break_warning = True if counts[0] > 0 else False
            rec.working_hours_warning = True if counts[1] > 0 else False

    def _search_no_break_warning(self, operator, value):
        res_ids = []
        for obj in self.search([]):
            if obj.no_break_warning is True:
                res_ids.append(obj.id)

        if (operator == '=' and value is True) or (operator == '!=' and value is False):
            operator = 'in'

        elif (operator == '!=' and True) or (operator == '=' and value is False):
            operator = 'not in'
        return [('id', operator, res_ids)]

    def _search_working_hours_warning(self, operator, value):
        res_ids = []
        for obj in self.search([]):
            if obj.working_hours_warning is True:
                res_ids.append(obj.id)

        if (operator == '=' and value is True) or (operator == '!=' and value is False):
            operator = 'in'

        elif (operator == '!=' and True) or (operator == '=' and value is False):
            operator = 'not in'
        return [('id', operator, res_ids)]

    no_break_warning = fields.Boolean('No break warning', compute=_compute_no_break_working_hours_warning, search=_search_no_break_warning)
    working_hours_warning = fields.Boolean('Working hours warning', compute=_compute_no_break_working_hours_warning, search=_search_working_hours_warning)

    @api.multi
    def write(self, vals):

        user_id = None
        old_user_id = self.employee_id.user_id.id
        if 'employee_id' in vals:
            emp_id = vals['employee_id']
            emp = self.env['hr.employee'].browse(emp_id)
            if emp.user_id:
                user_id = emp.user_id

        res = super(HrTimesheetSheet, self).write(vals)
        if user_id:
            for line in self.env['account.analytic.line'].search([('date', '<=', self.date_to),
                                                                  ('date', '>=', self.date_from),
                                                                  ('user_id', '=', old_user_id)]):
                line.user_id = user_id

        return res

    def copy(self, cr, uid, id, default=None, context=None):
        if context is None:
            context = {}
        context = context.copy()
        data = self.copy_data(cr, uid, id, default, context)
        emp = self.pool.get('hr.employee').browse(cr, uid, self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], limit=1))
        dep = emp.department_id
        data.update({'employee_id': emp.id, 'department_id': dep.id})

        if 'timesheet_ids' in self._fields:
            tmp_data = self.read(cr, uid, [id], ['timesheet_ids'], context=context)
            field = self._fields['timesheet_ids']
            other = self.pool[field.comodel_name]
            lines = [other.copy_data(cr, uid, line_id, context=context) for line_id in sorted(tmp_data[0]['timesheet_ids'])]
            for line in lines:
                if 'user_id' in line:
                    line['user_id'] = uid
                if 'department_id' in line:
                    line['department_id'] = dep.id
            data['timesheet_ids'] = [(0, 0, line) for line in lines if line]

        new_id = self.create(cr, uid, data, context)
        self.copy_translations(cr, uid, id, new_id, context)
        return new_id
