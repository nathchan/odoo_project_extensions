# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    planning_package = fields.Selection([(1, 'Planning package for equipment swap'),
                                         (2, 'Planning package small'),
                                         (3, 'Planning package medium'),
                                         (4, 'Planning package large')], 'Planning package')
    site_acquisition_package = fields.Selection([(1, 'Site acquisitions small'),
                                                 (2, 'Site acquisitions medium'),
                                                 (3, 'Site acquisitions large'),
                                                 (4, 'Site acquisitions for new construction')], 'SA package')

    civil_works_package = fields.Selection([(1, 'Rooftop site extension'),
                                            (2, 'New Rooftop Outdoor site'),
                                            (3, 'New Rooftop Indoor site'),
                                            (4, 'Greenfield site extension'),
                                            (5, 'New Greenfield Outdoor site'),
                                            (6, 'Moving sharing partner'),
                                            (7, 'Site deconstruction')], 'CW package')
