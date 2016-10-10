# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Project group',
    'version': '1.0',
    'summary': 'Lets you to projects in groups',
    'author': 'B++',
    'website': 'http://www.bplus.plus',
    'category': 'Projects',
    'images': [],
    'depends': [
        'project',
    ],
    'data': [
        'views/project_group_view.xml',
        'views/project_view.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    #'application': False,
    #'auto_install': False,
}