# -*- coding: utf-8 -*-
from odoo import (
    models,
    fields,
    api
)
from odoo.exceptions import UserError
import logging

logger = logging.getLogger(__name__)


class Presupuesto(models.Model):
    _name = 'presupuesto'
    _inherit = ['image.mixin']

    @api.depends('detalle_ids')
    def _compute_total(self):
        for record in self:
            sub_total = 0
            for linea in record.detalle_ids:
                sub_total += linea.importe
            record.base = sub_total
            record.impuestos = sub_total * 0.18
            record.total = sub_total * 1.18


    name = fields.Char(string='Pelicula')
    clasificacion = fields.Selection(selection=[
        ('G', 'G'), # publico en general
        ('PG', 'PG'), # compa;ia de un adulto
        ('PG13', 'PG13'), # mayores de 13 a;os
        ('R', 'R'), # Adulto obligatorio
        ('NC-17', 'NC-17') # Mayores de 18
    ], string="Clasificacion")
    puntuacion = fields.Integer(string="Puntuacion", related='puntuacion2')
    puntuacion2 = fields.Integer(string="Puntuacion2")
    fecha_estreno = fields.Date(string="Fecha Estreno")
    active = fields.Boolean(string="Activo", default=True)
    director_id = fields.Many2one(
        comodel_name='res.partner',
        string='Director'
    )
    categoria_director_id = fields.Many2one(
        comodel_name='res.partner.category',
        string='Categoria Autor',
        default=lambda self: self.env.ref('movies.category_director')
        # default=lambda self: self.env['res.partner.category'].search([('name', '=', 'Director')])
    )
    genero_ids = fields.Many2many(
        comodel_name='genero',
        string='Generos'
    )
    descripcion_clasificacion = fields.Char(string='Descripcion Clasificacion')
    vista_general = fields.Text(string='Descripcion')
    link_trailer = fields.Char(string="Trailer")
    es_libro = fields.Boolean(string="Version Libro")
    libro = fields.Binary(string='Libro')
    libro_filename = fields.Char(string='Nombre del libro')
    state = fields.Selection(
        selection=[
            ('borrador', 'Borrador'),
            ('aprobado', 'Aprobado'),
            ('cancelado', 'Cancelado')
        ],
        default='borrador',
        string='Estado',
        copy=False
    )
    fecha_aprobado = fields.Datetime(
        string='Fecha aprobado',
        copy=False
    )
    actores_id = fields.Many2many(
        comodel_name='res.partner',
        string='Actores'
    )
    actores_categoria_id = fields.Many2one(
        comodel_name='res.partner.category',
        string='Categoria Actor',
        default=lambda self: self.env.ref('movies.category_autor')
        # default=lambda self: self.env['res.partner.category'].search([('name', '=', 'Director')])
    )
    opinion = fields.Html(
        string='Opinion'
    )
    numero_presupuesto = fields.Char(
        string='Numero presupuesto',
        copy=False
    )
    fecha_creacion = fields.Datetime(
        string='Fecha creacion',
        copy=False,
        default=lambda self: fields.Datetime.now()
    )
    detalle_ids = fields.One2many(
        comodel_name='presupuesto.detalle',
        inverse_name='presupuesto_id',
        string='Presupuesto id'
    )
    campos_ocultos = fields.Boolean('Campos ocultos')
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id.id
    )
    terminos = fields.Text(string='Terminos')
    base = fields.Monetary(
        string='Base imponible',
        compute='_compute_total'
    )
    impuestos = fields.Monetary(
        string='Impuestos',
        compute='_compute_total'
    )
    total = fields.Monetary(
        string='Total',
        compute='_compute_total'
    )

    def unlink(self):
        for record in self:
            if record.state != 'cancelado':
                raise UserError('No se encuentrada en el estado cancelado')
            super(Presupuesto, record).unlink()

    @api.model
    def create(self, vals_list):
        logger.info(vals_list)
        sequence = self.env['ir.sequence']
        correlativo = sequence.next_by_code('secuencia.presupuesto.pelicula')
        vals_list['numero_presupuesto'] = correlativo
        return super(Presupuesto, self).create(vals_list)

    def write(self, vals):
        if vals.get('clasificacion'):
            raise UserError('La clasificacion no se pude editar')
        return super(Presupuesto, self).write(vals)

    def aprobar_presupuesto(self):
        self.state = 'aprobado'
        self.fecha_aprobado = fields.Datetime.now()

    def cancelar_presupuesto(self):
        self.state = 'cancelado'

    def copy(self, default=None):
        default = dict(default or {})
        default['name'] = f'{self.name} (Copia)'
        default['puntuacion2'] = 1
        return super(Presupuesto, self).copy(default)
    
    @api.onchange('clasificacion')
    def _onchange_clasificacion(self):
        if self.clasificacion:
            if self.clasificacion == 'G':
                self.descripcion_clasificacion = 'Publico General'
            if self.clasificacion == 'PG':
                self.descripcion_clasificacion = 'Compa;oa de adulto'
            if self.clasificacion == 'PG13':
                self.descripcion_clasificacion = 'Mayores de 13 a;os'
            if self.clasificacion == 'R':
                self.descripcion_clasificacion = 'Solo para mayores de edad'
            if self.clasificacion == 'NC-17':
                self.descripcion_clasificacion = 'Mayores de 18'


class PresupuestoDetalle(models.Model):
    _name = "presupuesto.detalle"


    presupuesto_id = fields.Many2one(
        comodel_name='presupuesto',
        string='presupuesto'
    )
    name = fields.Many2one(
        comodel_name='recurso.cinematrogafico',
        string='Recurso'
    )
    descripcion = fields.Char(
        string='Descripcion',
        related='name.descripcion'
    )
    precio = fields.Float(
        string='Precio',
        digits='Product Price'
    )
    contacto_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contacto',
        related='name.contacto_id'
    )
    imagen = fields.Binary(
        string='Imagen',
        related='name.imagen'
    )
    cantidad = fields.Float(
        string='Cantidad',
        default=1.0,
        digits=(16, 4)
    )
    importe = fields.Monetary(string='Importe')
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Moneda',
        related='presupuesto_id.currency_id'
    )

    @api.onchange('name')
    def _onchange_name(self):
        if self.name:
            self.precio = self.name.precio

    @api.onchange('cantidad', 'precio')
    def _onchange_importe(self):
        self.importe = self.cantidad * self.precio