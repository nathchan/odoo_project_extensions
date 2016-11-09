# -*- coding: utf-8 -*-

from openerp import models, fields, api

class HrTimesheetSheet(models.Model):
    _inherit = 'hr_timesheet_sheet.sheet'


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
            for line in self.env['account.analytic.line'].search([('date', '<=', self.date_to), ('date', '>=', self.date_from),
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
