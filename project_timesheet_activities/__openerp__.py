# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Project timesheet activities',
    'version': '1.0',
    'summary': 'Enables detailed input of employee activities',
    'author': 'B++',
    'website': 'http://www.bplus.plus',
    'category': 'Projects',
    'images': [],
    'depends': [
        'project',
        'project_issue',
        'project_issue_sheet',
        'project_timesheet',
        'hr_timesheet_sheet',
    ],
    'data': [
        'views/project_activity_view.xml',
        'views/task_view.xml',
        'views/timesheet_view.xml',
        'views/hr_timesheet_sheet_view.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    #'application': False,
    #'auto_install': False,
}