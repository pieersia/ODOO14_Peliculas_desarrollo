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
        default=lambda  self: self.env['res.partner.category'].search([('name', '=', 'director')])

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
        if  self.state != 'cancelado':
            raise UserError('No se puede eliminar el registro, porque no se encuentra en estado cancelado')
        super(Presupuesto, self).unlink()

    @api.model
    def create(self, variables):
        logger.info('********** variables: {0}'.format(variables))
        return super(Presupuesto, self).create(variables)

    def write(self, variables):
        logger.info('********** variables: {0}'.format(variables))
        if 'clasification' in variables:
            raise UserError('La clasificacion no se puede editar !! ')
        return super(Presupuesto, self).write(variables)

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
