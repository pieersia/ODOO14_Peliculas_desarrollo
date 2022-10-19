# -*- coding:utf-8 -*-
import logging
from odoo import fields, models, api
#from odoo.odoo.exceptions import UserError #mostrar los mensajes de error en codigo
from odoo.exceptions import UserError #mostrar los mensajes de error en odoo

logger=logging.getLogger(__name__)
#de la clase empieza con Mayudascula "P" Presupuesto - a eso se le llama tipo camello
class Presupuesto(models.Model):
    #crea la tabla presupuesto en la BD
    _name = "presupuesto"
    _inherit = ['image.mixin'] #crear imagen

    #crea el campo dentro de la tabla
    name = fields.Char(string='Pelicula')
    gasto = fields.Float(string='gasto')
    #crea un campo de clasificacion dentro de la tabla
    #(a,b)  la "a" llega a la BD, la "b" es lo que se muestra en la interfaz
    clasification = fields.Selection(selection = [
        ('G', 'Publico General'), #Publico general
        ('PG', 'PG'), #Se recomienda la compania de un adulto
        ('PG-13', 'PG-13'), #Mayores de 13
        ('R', 'R'), #En compania de un adulto obligatorio
        ('NC-17', 'NC-17') #Mayores de 18
    ], string='Clasificación')

    dsc_clasification = fields.Char(String='Descripcion clasificacion')
    fch_estreno = fields.Date(string='Fecha de Estreno')
    puntuacion = fields.Integer(string='Puntuación', related="puntuacion2")
    #puntuacion2 es una copia de puntuacion para que los 2 valores sean iguales
    puntuacion2 = fields.Integer(string='Puntuacion2')
    #no es recomendable borrar datos de la BD
    #por eso, active oculta datos a la vista del usuario para que no se elimine
    active = fields.Boolean(string='Activo', default=True)   #default, para que aparesca activo

    ''' CODIGO PARA RELACIONAR BASE DE DATOS MANY 2 ONE '''

    director_id = fields.Many2one(
        comodel_name = 'res.partner',# res.partner es lo que aparece en el link model=res.partner,es la tabla
        string='Director'

    )
    categoria_director_id = fields.Many2one(
        comodel_name='res.partner.category',
        string='Categoria Director',

        #Version 2
        default=lambda self: self.env.ref('peliculas.category_director')

        #Version 1
        #default=lambda  self: self.env['res.partner.category'].search([('name', '=', 'director')])

    )
    # //////    GENEROS /////////////#
    actor_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Actores'
    )
    actor_director_id = fields.Many2one(
        comodel_name='res.partner.category',
        string='Categoria Actor',
        default=lambda self: self.env.ref('peliculas.category_actor')
    )


    ''' CODIGO PARA RELACIONAR BASE DE DATOS MANY 2 MANY'''
    genero_ids = fields.Many2many(
        comodel_name = 'genero',
        string='Géneros'
    )

    vista_general = fields.Text(string='Descripción')
    link_trailer = fields.Char(string='Trailer')
    es_libro = fields.Boolean(string='Version Libro')
    libro = fields.Binary(string='Libro')
    libro_filename= fields.Char(string='Nombre del libro')


    state = fields.Selection(selection=[('borrador', 'Borrador'),('aprobado', 'Aprobado'),
                                        ('cancelado', 'Cancelado'),
                             ], default='borrador', string='Estados', copy=False)
    fch_aprobado = fields.Datetime(string='Fecha aprobado', copy=False)
    fch_publicado = fields.Datetime(string='Fecha publicado', copy=False, default=lambda self: fields.Datetime.now())
    numero_presupuesto = fields.Char(string='Numero Presupuesto', copy=False)
    opinion = fields.Html(string='Opinion')
    detalle_ids = fields.One2many(
        comodel_name='presupuesto.detalle',
        inverse_name='presupuesto_id',
        string='Detalles',
    )
    campos_ocultos = fields.Boolean(string='Campos Ocultos')

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id.id,
    )
    terminos = fields.Text(string='Terminos')
    base = fields.Monetary(string='Base imponible', compute='_compute_total')
    impuestos = fields.Monetary(string='Impuestos', compute='_compute_total')
    total = fields.Monetary(string='Total', compute='_compute_total')
    

    def aprobar_presupuesto(self):
        logger.info('Entro a la funcion aprobar presupuesto')
        self.state = 'aprobado'
        #poner fecha actual
        self.fch_aprobado = fields.Datetime.now()

    def cancelar_presupuesto(self):
        self.state = 'cancelado'

    #sobre escribir odoo
    ''' metodo 2 '''
    def unlink(self):
        logger.info('************** se disparo la funcion unlink')
        #--Version 2 para eliminar varios registros
        #1ro, va un for record, 2do, se cambia el self por el record
        for record in self:
            if record.state != 'cancelado':
                raise UserError('No se puede eliminar el registro, porque no se encuentra en estado cancelado')
            super(Presupuesto, record).unlink()

        # ---  version 1  cuando se elimina solo 1 archivo --------
        # if  self.state != 'cancelado':
        #     raise UserError('No se puede eliminar el registro, porque no se encuentra en estado cancelado')
        # super(Presupuesto, self).unlink()
        #--- este es el error ValueError: Expected singleton: presupuesto(4, 5, 6, 9, 10)---
        #-----------------------------------------------------------


    @api.model
    def create(self, variables):
        logger.info('********** variables: {0}'.format(variables))
        #---- correlativos para documentos ---
        sequence_obj = self.env['ir.sequence']
        correlativo = sequence_obj.next_by_code('secuencia.presupuesto.pelicula')
        variables['numero_presupuesto'] = correlativo
        #-----------------------------------------------------------------------
        return super(Presupuesto, self).create(variables)

    def write(self, variables):
        logger.info('********** variables: {0}'.format(variables))
        if 'clasification' in variables:
            raise UserError('La clasificacion no se puede editar !! ')
        return super(Presupuesto, self).write(variables)

    def copy(self, default = None):
        default = dict(default or {})
        default['name'] = self.name + ' (copia)'
        default['puntuacion2'] = 1
        default['clasification'] = 'NC-17'

        return super(Presupuesto, self).copy(default)

    @api.onchange('clasification')
    def _onchange_clasification(self):
        if self.clasification:
            if self.clasification == 'G':
                self.dsc_clasification='Publico General'
            if self.clasification == 'PG':
                self.dsc_clasification='Pokemon Go'
            if self.clasification == 'PG-13':
                self.dsc_clasification='Pokemon Go 13'
            if self.clasification == 'R':
                self.dsc_clasification='Ratata'
            if self.clasification == 'NC-17':
                self.dsc_clasification='Nota de Credito 17'
        else:
            self.dsc_clasification = False



    '''  METODO 1 
    def unlink(self):
        logger.info('************** se disparo la funcion unlink')
        #para eliminar registro desde la bd, llamar al padre super
        # eliminar registros solo en estado cancelado
        if self.state == "cancelado":
            super(Presupuesto, self).unlink()
            logger.info('************** Se elimino exitosamente')
        else:
            raise UserError('No se puede eliminar el registro, porque no se encuentra en estado cancelado')
            #logger.info('************** No se puede eliminar, por que no se encuentra en el estado cancelado')
    '''
class PresupuestoDetalle(models.Model):
    _name = "presupuesto.detalle"

    presupuesto_id = fields.Many2one(
        comodel_name='presupuesto',
        string='Presupuesto'
    )
    name = fields.Many2one(
        comodel_name='recurso.cinematografico',
        string='Recurso'
    )
    descripcion = fields.Char(
        string='Descripcion',
        related='name.descripcion'
    )
    contacto_id=fields.Many2one(
        comodel_name='res.partner',
        string='Contacto',
        related='name.contacto_id'
    )
    imagen = fields.Binary(string='Imagen', related='name.imagen')
    cantidad = fields.Float(string='Cantidad', default='1.0', digits=(16,4))
    precio = fields.Float(string='Precio', digits='Product Price')
    importe = fields.Monetary(string='Importe')

    #esto siempre va se se usa multimoneda
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

