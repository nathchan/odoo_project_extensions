# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Warehouse and Project integration',
    'version': '1.0',
    'summary': 'Warehouse and Project integration',
    'author': 'nemanja-d@hotmail.com',
    'website': 'https://www.linkedin.com/in/nemanjadragovic',
    'category': 'Projects',
    'images': [],
    'depends': [
        'project',
        'stock',
        'purchase'
    ],
    'data': [
        'views/purchase_order_view.xml',
        'views/stock_picking_view.xml'
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    #'application': False,
    #'auto_install': False,
}