# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'New view for All timesheets',
    'version': '1.0',
    'summary': 'Enables managers to see all timesheets',
    'author': 'nemanja-d@hotmail.com',
    'website': 'https://www.linkedin.com/in/nemanjadragovic',
    'category': 'Human Resources',
    'images': [],
    'depends': [
        'hr_timesheet_sheet',
    ],
    'data': [
        'views/timesheet_sheet.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    #'application': False,
    #'auto_install': False,
}