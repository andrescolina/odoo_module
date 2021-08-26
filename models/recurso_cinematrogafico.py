# -*- coding: utf-8 -*-
from odoo import (
    models,
    fields,
    api
)

class RecursoCinamatrogafico(models.Model):
    _name = 'recurso.cinematrogafico'

    name = fields.Char(string='Recurso')
    descripcion = fields.Char(string='Descripcion')
    precio = fields.Float(string='Precio')
    contacto_id = fields.Many2one(
        comodel_name='res.partner',
        domain="[('is_company', '=', False)]"
    )
    imagen = fields.Binary(string='Imagen')