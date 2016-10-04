# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Task forecasts',
    'version': '1.0',
    'summary': 'Lets you to create forecasts for task lifecycle',
    'author': 'B++',
    'website': 'http://www.bplus.plus',
    'category': 'Projects',
    'images': [],
    'depends': [
        'project',
        'project_default_stages',
    ],
    'data': [
        'views/task_view.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    #'application': False,
    #'auto_install': False,
}