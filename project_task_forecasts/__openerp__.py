# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Task forecasts',
    'version': '1.0',
    'summary': 'Lets you to create forecasts for task lifecycle',
    'author': 'nemanja-d@hotmail.com',
    'website': 'https://www.linkedin.com/in/nemanjadragovic',
    'category': 'Projects',
    'images': [],
    'depends': [
        'project',
        'project_default_stages',
    ],
    'data': [
        'views/assets_backend.xml',
        'views/task_view.xml',
        'views/task_type_view.xml',
        'views/task_stage_forecast.xml',
        'views/stage_process_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    #'application': False,
    #'auto_install': False,
}