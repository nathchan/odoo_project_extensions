# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools, exceptions as e
import datetime

class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    def _populate_emp_manager_list(self, employee_id, list):
        if employee_id.parent_id and employee_id.parent_id.user_id:
            list.append(employee_id.parent_id.user_id.id)
            self._populate_emp_manager_list(employee_id.parent_id, list)

    def _populate_child_dep_list(self, department_id, list):
        if department_id.child_ids and len(department_id.child_ids) > 0:
            for child in department_id.child_ids:
                list.append(child.id)
                self._populate_child_dep_list(child, list)

    def _populate_child_emp_list(self, employee_id, list):
        child_emps = self.env['hr.employee'].search([('parent_id', '=', employee_id.id)])
        if child_emps and len(child_emps) > 0:
            for child in child_emps:
                list.append(child.id)
                self._populate_child_emp_list(child, list)

    def _search_manager(self, operator, value):
        if operator != '=':
            return [('id', 'in', [])]

        emps = self.env['hr.employee'].search([('user_id', '=', value)])
        emp_list = [emp.id for emp in emps]
        for emp in emps:
            child_emps = self.env['hr.employee'].search([('parent_id', '=', emp.id)])
            for ch_emp in child_emps:
                emp_list.append(ch_emp.id)
                self._populate_child_emp_list(ch_emp, emp_list)

        return [('employee_id', 'in', emp_list)]

    @api.depends('number_of_days_temp')
    @api.multi
    def _compute_num_of_days_to_display(self):
        for rec in self:
            rec.number_of_days_to_display = rec.number_of_days_temp

    @api.multi
    def _compute_manager_fields(self):
        for rec in self:
            rec.manager = 0

    # @api.one
    # def _compute_display_emp_domain_field(self):
    #     if self.env.user.has_group('base.group_hr_user'):
    #         self.display_employee_field_with_domain = False
    #     else:
    #         self.display_employee_field_with_domain = True
    #
    # def _default_display_emp_domain_field(self):
    #     if self.env.user.has_group('base.group_hr_user'):
    #         return False
    #     else:
    #         return True

    date_from = fields.Date('Start Date', readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, select=True, copy=False)
    date_to = fields.Date('End Date', readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, copy=False)
    number_of_days_to_display = fields.Integer('Duration to display', compute=_compute_num_of_days_to_display)
    manager = fields.Integer('Manager', compute=_compute_manager_fields, search=_search_manager)
    # display_employee_field_with_domain = fields.Boolean('Display emp field with domain', compute=_compute_display_emp_domain_field, default=_default_display_emp_domain_field)
    # employee_with_domain = fields.Many2one('hr.employee', 'Employee with domain')

    # @api.onchange('employee_with_domain')
    # @api.one
    # def change_employee_with_domain(self):
    #     if self.employee_with_domain:
    #         self.employee_id = self.employee_with_domain

    @api.one
    def holidays_validate(self):
        if self.type == 'remove' and self.env.user.id != tools.SUPERUSER_ID:
            if not self.env.user.has_group('base.group_hr_user'):
                raise e.ValidationError('You are not allowed to approve leave requests.')

            emp_manager_list = []
            self._populate_emp_manager_list(self.employee_id, emp_manager_list)
            if not (self.env.user.id in emp_manager_list):
                raise e.ValidationError('You are not allowed to approve leave request for '+ self.employee_id.name + '.')

        super(HrHolidays, self).holidays_validate()


    @api.onchange('date_from', 'date_to')
    @api.one
    def calculate_number_of_days(self):
        self.number_of_days_temp = 0
        if self.date_from and self.date_to and self.date_from <= self.date_to:
            current_date = datetime.datetime.strptime(self.date_from, tools.DEFAULT_SERVER_DATE_FORMAT)
            end_date = datetime.datetime.strptime(self.date_to, tools.DEFAULT_SERVER_DATE_FORMAT)
            days_sum = 0
            while current_date <= end_date:
                count = self.env['hr.day.off'].search([('date', '=', current_date.strftime(tools.DEFAULT_SERVER_DATE_FORMAT))], count=True)
                if count == 0:
                    days_sum += 1
                current_date = current_date + datetime.timedelta(days=1)
            self.number_of_days_temp = days_sum

    @api.onchange('holiday_status_id')
    @api.one
    def onchange_holiday_status(self):
        self.name = ''
        if self.holiday_status_id:
            self.name = self.holiday_status_id.name