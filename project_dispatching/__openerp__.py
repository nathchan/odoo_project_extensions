# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Dispatching Projects',
    'version': '1.0',
    'summary': 'Dispatching resources on projects and tasks',
    'author': 'nemanja-d@hotmail.com',
    'website': 'https://www.linkedin.com/in/nemanjadragovic',
    'category': 'Projects',
    'images': [],
    'depends': [
        'project',
        'hr',
        'fleet',
        'project_timesheet_activities',
        'project_task_issues',
        'project_task_forecasts',
        'project_security',
    ],
    'data': [
        'views/project_dispatching_view.xml',
        'views/project_task_view.xml',
        'views/timesheet_view.xml',
        'views/menuitem.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    #'application': False,
    #'auto_install': False,
}