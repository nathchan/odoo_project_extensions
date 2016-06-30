# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Project manager on kanban',
    'version': '1.0',
    'summary': 'Shows project manager name on kanban view',
    'author': 'B++',
    'website': 'http://www.bplus.plus',
    'category': 'Projects',
    'images': [],
    'depends': [
        'project'
    ],
    'data': [
        'views/project_view.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    #'application': False,
    #'auto_install': False,
}