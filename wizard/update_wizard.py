# -*- coding: utf-8 -*-
from odoo import (
    models,
    fields,
    api
)
import logging

logger = logging.getLogger(__name__)


class UpdateWizard(models.TransientModel):
    _name = 'update.wizard'

    name = fields.Text(string='Nueva descripcion')

    def update_vista_general(self):
        presupuesto_object = self.env['presupuesto']
        # presupuesto_id = presupuesto_object.search([('id', '=', self._context['active_id'])])
        presupuesto_id = presupuesto_object.browse(self._context['active_id'])
        presupuesto_id.vista_general = self.name