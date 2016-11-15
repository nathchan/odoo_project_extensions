# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Project Task Packages',
    'version': '1.0',
    'summary': 'Allows to determine Package type for Task',
    'author': 'nemanja-d@hotmail.com',
    'website': 'https://www.linkedin.com/in/nemanjadragovic',
    'category': 'Projects',
    'images': [],
    'depends': [
        'project',
    ],
    'data': [
        'views/task_view.xml',
        'security/ir.model.access.csv',
        'data/res_partner.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    #'application': False,
    #'auto_install': False,
}