# -*- coding: utf-8 -*-
from odoo import (
    models,
    fields,
    api
)


class Genero(models.Model):
    _name = "genero"
    name = fields.Char()