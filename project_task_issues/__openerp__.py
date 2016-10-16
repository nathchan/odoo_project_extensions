# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Links issues for task',
    'version': '1.0',
    'summary': 'Enables preview of issues from task view',
    'author': 'nemanja-d@hotmail.com',
    'website': 'https://www.linkedin.com/in/nemanjadragovic',
    'category': 'Projects',
    'images': [],
    'depends': [
        'project',
        'project_issue_sheet',
        'project_issue',
    ],
    'data': [
        'views/task_view.xml',
        'views/issue_view.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    #'application': False,
    #'auto_install': False,
}