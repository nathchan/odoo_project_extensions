# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools, exceptions as e
import datetime
from dateutil import relativedelta

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
                            l.timesheet_sheet_id = %d
                            and not (acc.name = 'Urlaub / Holiday' or acc.name = 'Krankenstand / Illness')
                        group by
                            timesheet_sheet_id, date
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
                            l.timesheet_sheet_id = %d
                        group by
                            timesheet_sheet_id, date
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
                        l.timesheet_sheet_id = %d
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

    def _default_date_from_to(self):
        return datetime.datetime.now().strftime(tools.DEFAULT_SERVER_DATE_FORMAT)

    no_break_warning = fields.Boolean('No break warning', compute=_compute_no_break_working_hours_warning, search=_search_no_break_warning)
    working_hours_warning = fields.Boolean('Working hours warning', compute=_compute_no_break_working_hours_warning, search=_search_working_hours_warning)

    supervisor_must_approve = fields.Boolean('Supervisor must approve', compute=_compute_supervisor_must_approve, search=_search_supervisor_must_approve)

    date_from = fields.Date('Date from', default=_default_date_from_to)
    date_to = fields.Date('Date to', default=_default_date_from_to)

    timesheet_activity_ids = fields.One2many('account.analytic.line', 'timesheet_sheet_id', string='Activities')

    approved_status = fields.Selection([('new', 'New'),
                                       ('draft', 'Waiting Approval'),
                                       ('approved', 'Approved'),
                                       ('refused', 'Refused')], 'Approved State', default='new')

    @api.multi
    def button_submit_to_manager(self):
        for rec in self:
            if rec.no_break_warning is True:
                raise e.ValidationError("Timesheet with no break warning can't be submitted to manager.")
            rec.approved_status = 'draft'
            for line in rec.timesheet_activity_ids:
                if line.timesheet_approved_status == 'new' or line.timesheet_approved_status == 'refused':
                    line.timesheet_approved_status = 'draft'

    @api.multi
    def button_approve_all(self):
        for rec in self:
            rec.approved_status = 'approved'
            for line in rec.timesheet_activity_ids:
                line.timesheet_approved_status = 'approved'

    @api.multi
    def button_refuse_all(self):
        for rec in self:
            rec.approved_status = 'refused'
            for line in rec.timesheet_activity_ids:
                line.timesheet_approved_status = 'refused'

    @api.multi
    def button_duplicate(self):
        data = {}
        emp = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        data.update({
            'employee_id': emp.id,
            'user_id': emp.user_id.id,
            'department_id': emp.department_id.id,
            'date_from': self[0].date_from,
            'date_to': self[0].date_to,
        })
        if 'timesheet_activity_ids' in self._fields:
            tmp_data = self.read(['timesheet_activity_ids'])
            field = self._fields['timesheet_activity_ids']
            other = self.pool[field.comodel_name]
            lines = [other.copy_data(self.env.cr, self.env.user.id, line_id) for line_id in sorted(tmp_data[0]['timesheet_activity_ids'])]
            for line in lines:
                line['timesheet_approved_status'] = 'new'
                if 'user_id' in line:
                    line['user_id'] = self.env.user.id
                if 'department_id' in line:
                    line['department_id'] = emp.department_id.id
            data['timesheet_activity_ids'] = [(0, 0, line) for line in lines if line]
        #
        new_timesheet = self.create(data)
        action = {
            'type': 'ir.actions.act_window',
            'res_id': new_timesheet.id,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr_timesheet_sheet.sheet',
            'context': self.env.context,
        }
        return action

    @api.constrains('date_from', 'date_to')
    def sap_dates_constrains(self):
        if self.date_from and self.date_to and self.date_to < self.date_from:
            raise e.ValidationError('Date from must be before date to.')

    @api.model
    def create(self, vals):
        if 'date_from' in vals and self.env.user.id != tools.SUPERUSER_ID:
            first_day_of_week = datetime.datetime.now()+relativedelta.relativedelta(weekday=0, days=-6)
            date_from = datetime.datetime.strptime(vals['date_from'], tools.DEFAULT_SERVER_DATE_FORMAT)
            if date_from < first_day_of_week:
                raise e.ValidationError('Creation of timesheet for last week is forbidden. Please enter dates from current week.')

        res = super(HrTimesheetSheet, self).create(vals)
        return res

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
            for line in self.env['account.analytic.line'].search([('timesheet_sheet_id', '=', self.id)]):
                line.user_id = user_id

        return res

    def unlink(self, cr, uid, ids, context=None):
        sheets = self.read(cr, uid, ids, ['approved_status'], context=context)
        for sheet in sheets:
            if sheet['approved_status'] in ('approved'):
                raise e.UserError('You cannot delete a timesheet which is already confirmed.')

        to_remove = []
        analytic_timesheet = self.pool.get('account.analytic.line')
        for sheet in self.browse(cr, uid, ids, context=context):
            for timesheet in sheet.timesheet_activity_ids:
                to_remove.append(timesheet.id)
        analytic_timesheet.unlink(cr, uid, to_remove, context=context)

        return super(HrTimesheetSheet, self).unlink(cr, uid, ids, context=context)

    def copy(self, cr, uid, id, default=None, context=None):
        raise e.UserError('For duplicate, please use Duplicate button below this one.')
