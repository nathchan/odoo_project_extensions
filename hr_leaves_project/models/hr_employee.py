# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools, exceptions as e
import datetime

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _compute_manager_fields(self):
        for rec in self:
            rec.manager = 0

    def _populate_child_emp_list(self, employee_id, list):
        child_emps = self.search([('parent_id', '=', employee_id.id)])
        if child_emps and len(child_emps) > 0:
            for child in child_emps:
                list.append(child.id)
                self._populate_child_emp_list(child, list)

    def _search_manager(self, operator, value):
        if operator != '=':
            return [('id', 'in', [])]

        emps = self.search([('user_id', '=', value)])
        emp_list = [emp.id for emp in emps]
        for emp in emps:
            child_emps = self.search([('parent_id', '=', emp.id)])
            for ch_emp in child_emps:
                emp_list.append(ch_emp.id)
                self._populate_child_emp_list(ch_emp, emp_list)

        return [('id', 'in', emp_list)]

    manager = fields.Integer('Hierarchy Manager', compute=_compute_manager_fields, search=_search_manager)