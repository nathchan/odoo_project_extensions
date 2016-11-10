# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'HR holiday days',
    'version': '1.0',
    'summary': 'Module to mark holiday days',
    'author': 'nemanja-d@hotmail.com',
    'website': 'https://www.linkedin.com/in/nemanjadragovic',
    'category': 'Human Resources',
    'images': [],
    'depends': [
        'hr',
    ],
    'data': [
        'views/hr_day_off_category_view.xml',
        'views/hr_day_off_view.xml',
        'wizard/hr_weekend_generator_view.xml',
        'views/menuitems.xml',
        'security/ir.model.access.csv',
        'data/hr_day_off_category_data.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    #'application': False,
    #'auto_install': False,
}