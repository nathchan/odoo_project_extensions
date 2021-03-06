# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'HR Leaves and Project integration',
    'version': '1.0',
    'summary': 'Integration of modules Project and HR Leaves',
    'author': 'nemanja-d@hotmail.com',
    'website': 'https://www.linkedin.com/in/nemanjadragovic',
    'category': 'Projects',
    'images': [],
    'depends': [
        'project',
        'hr_holidays',
        'hr_holiday_days',
    ],
    'data': [
        'views/hr_holidays_view.xml',
        'views/hr_holidays_status_view.xml',
        'views/hr_employee_view.xml',
        'views/menuitems.xml',
        'security/res_group.xml',
        'security/ir_rule.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    #'application': False,
    #'auto_install': False,
}