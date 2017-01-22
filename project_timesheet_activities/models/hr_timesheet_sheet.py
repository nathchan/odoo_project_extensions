# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools, exceptions as e
import datetime

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
                            left join account_analytic_account acc on acc.id = l.account_id
                        where
                            l.sheet_id = %d
                            and not (acc.name = 'Urlaub / Holiday' or acc.name = 'Krankenstand / Illness')
                        group by
                            sheet_id, date
                        having
                            sum(unit_amount) >= 6.0
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
                            sum(unit_amount) > 10.5
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

    @api.multi
    def _compute_supervisor_must_approve(self):
        for rec in self:
            db = self.env.cr
            break_query = """
                select
                (
                    select
                        count(*)
                    from
                        account_analytic_line l
                        left join project_task t on t.id = l.task_id
                    where
                        l.sheet_id = %d
                        and t.user_id = %d
                        and l.timesheet_approved_status in ('draft')
                ) as warning
            """
            db.execute(break_query % (rec.id, self.env.user.id,))
            counts = db.fetchone()
            rec.supervisor_must_approve = True if counts[0] > 0 else False

    def _search_supervisor_must_approve(self, operator, value):
        res_ids = []
        for obj in self.search([]):
            if obj.supervisor_must_approve is True:
                res_ids.append(obj.id)

        if (operator == '=' and value is True) or (operator == '!=' and value is False):
            operator = 'in'

        elif (operator == '!=' and True) or (operator == '=' and value is False):
            operator = 'not in'
        return [('id', operator, res_ids)]

    no_break_warning = fields.Boolean('No break warning', compute=_compute_no_break_working_hours_warning, search=_search_no_break_warning)
    working_hours_warning = fields.Boolean('Working hours warning', compute=_compute_no_break_working_hours_warning, search=_search_working_hours_warning)

    supervisor_must_approve = fields.Boolean('Supervisor must approve', compute=_compute_supervisor_must_approve, search=_search_supervisor_must_approve)

    date_from = fields.Date('Date from', default=datetime.datetime.now().strftime(tools.DEFAULT_SERVER_DATE_FORMAT))
    date_to = fields.Date('Date to', default=datetime.datetime.now().strftime(tools.DEFAULT_SERVER_DATE_FORMAT))

    # @api.multi
    # @api.depends('timesheet_ids.timesheet_approved_status', 'timesheet_ids.unit_amount', 'timesheet_ids.timesheet_break_amount')
    # def _compute_approved_status(self):
    #     for rec in self:
    #         if len(rec.timesheet_ids) == len(rec.timesheet_ids.filtered(lambda r: r.timesheet_approved_status == 'new')):
    #             rec.approved_status = 'new'
    #         elif len(rec.timesheet_ids) == len(rec.timesheet_ids.filtered(lambda r: r.timesheet_approved_status == 'draft')):
    #             rec.approved_status = 'draft'
    #         elif rec.no_break_warning == False and rec.working_hours_warning == False and len(rec.timesheet_ids) == len(rec.timesheet_ids.filtered(lambda r: r.timesheet_approved_status == 'approved')):
    #             rec.approved_status = 'approved'
    #         else:
    #             rec.approved_status = 'refused'

    approved_status = fields.Selection([('new', 'New'),
                                       ('draft', 'Waiting Approval'),
                                       ('approved', 'Approved'),
                                       ('refused', 'Refused')], 'Approved State')

    @api.multi
    def button_submit_to_manager(self):
        for rec in self:
            if rec.no_break_warning is True:
                raise e.ValidationError("Timesheet with no break warning can't be submitted to manager.")
            rec.approved_status = 'draft'
            for line in rec.timesheet_ids:
                if line.timesheet_approved_status == 'new' or line.timesheet_approved_status == 'refused':
                    line.timesheet_approved_status = 'draft'

    @api.multi
    def button_approve_all(self):
        for rec in self:
            rec.approved_status = 'approved'
            for line in rec.timesheet_ids:
                line.timesheet_approved_status = 'approved'

    @api.multi
    def button_refuse_all(self):
        for rec in self:
            rec.approved_status = 'refused'
            for line in rec.timesheet_ids:
                line.timesheet_approved_status = 'refused'

    @api.one
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
