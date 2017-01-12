# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Project timesheet activities',
    'version': '1.0',
    'summary': 'Enables detailed input of employee activities',
    'author': 'nemanja-d@hotmail.com',
    'website': 'https://www.linkedin.com/in/nemanjadragovic',
    'category': 'Projects',
    'images': [],
    'depends': [
        'project',
        'project_issue',
        'project_issue_sheet',
        'project_timesheet',
        'hr_timesheet_sheet',
        'hr_holiday_days',
        'fleet',
    ],
    'data': [
        'security/security.xml',
        'views/project_activity_view.xml',
        'views/task_view.xml',
        'views/timesheet_view.xml',
        'views/hr_timesheet_sheet_view.xml',
        'wizard/employee_timesheet_generator_view.xml',
        'views/hr_timesheet_menuitem.xml',
        'views/hr_my_timesheets_action.xml',
        'views/account_analytic_account_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    #'application': False,
    #'auto_install': False,
}