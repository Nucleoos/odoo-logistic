# -*- coding: utf-8 -*-


from openerp import models, fields
from openerp.exceptions import Warning
from openerp.tools.translate import _


class waybill(models.Model):

    """"""

    _inherit = 'logistic.waybill'

    def _get_initial_odometer(self, cr, uid, ids, initial_odometer_id, arg, context):
        res = dict.fromkeys(ids, False)
        for record in self.browse(cr, uid, ids, context=context):
            if record.initial_odometer_id:
                res[record.id] = record.initial_odometer_id.value
        return res

    def _set_initial_odometer(self, cr, uid, id, name, value, args=None, context=None):
        if not value:
            # raise except_orm(_('Operation not allowed!'), _('Emptying the odometer value of a vehicle is not allowed.'))
            return True
        date = self.browse(cr, uid, id, context=context).date
        if not(date):
            date = fields.date.context_today(self, cr, uid, context=context)
        vehicle_id = self.browse(cr, uid, id, context=context).tractor_id
        data = {'value': value, 'date': date, 'vehicle_id': vehicle_id.id}
        odometer_id = self.pool.get('fleet.vehicle.odometer').create(
            cr, uid, data, context=context)
        return self.write(cr, uid, id, {'initial_odometer_id': odometer_id}, context=context)

    def _get_final_odometer(self, cr, uid, ids, final_odometer_id, arg, context):
        res = dict.fromkeys(ids, False)
        for record in self.browse(cr, uid, ids, context=context):
            if record.final_odometer_id:
                res[record.id] = record.final_odometer_id.value
        return res

    def _set_final_odometer(self, cr, uid, id, name, value, args=None, context=None):
        if not value:
            # raise except_orm(_('Operation not allowed!'), _('Emptying the odometer value of a vehicle is not allowed.'))
            return True
        date = self.browse(cr, uid, id, context=context).date
        if not(date):
            date = fields.date.context_today(self, cr, uid, context=context)
        vehicle_id = self.browse(cr, uid, id, context=context).tractor_id
        data = {'value': value, 'date': date, 'vehicle_id': vehicle_id.id}
        odometer_id = self.pool.get('fleet.vehicle.odometer').create(
            cr, uid, data, context=context)
        return self.write(cr, uid, id, {'final_odometer_id': odometer_id}, context=context)

    # WAGON
    def _get_wagon_initial_odometer(self, cr, uid, ids, wagon_initial_odometer_id, arg, context):
        res = dict.fromkeys(ids, False)
        for record in self.browse(cr, uid, ids, context=context):
            if record.wagon_initial_odometer_id:
                res[record.id] = record.wagon_initial_odometer_id.value
        return res

    def _set_wagon_initial_odometer(self, cr, uid, id, name, value, args=None, context=None):
        if not value:
            # raise except_orm(_('Operation not allowed!'), _('Emptying the odometer value of a vehicle is not allowed.'))
            return True
        date = self.browse(cr, uid, id, context=context).date
        if not(date):
            date = fields.date.context_today(self, cr, uid, context=context)
        vehicle_id = self.browse(cr, uid, id, context=context).wagon_id
        data = {'value': value, 'date': date, 'vehicle_id': vehicle_id.id}
        odometer_id = self.pool.get('fleet.vehicle.odometer').create(
            cr, uid, data, context=context)
        return self.write(cr, uid, id, {'wagon_initial_odometer_id': odometer_id}, context=context)

    def _get_wagon_final_odometer(self, cr, uid, ids, wagon_final_odometer_id, arg, context):
        res = dict.fromkeys(ids, False)
        for record in self.browse(cr, uid, ids, context=context):
            if record.wagon_final_odometer_id:
                res[record.id] = record.wagon_final_odometer_id.value
        return res

    def _set_wagon_final_odometer(self, cr, uid, id, name, value, args=None, context=None):
        if not value:
            # raise except_orm(_('Operation not allowed!'), _('Emptying the odometer value of a vehicle is not allowed.'))
            return True
        date = self.browse(cr, uid, id, context=context).date
        if not(date):
            date = fields.date.context_today(self, cr, uid, context=context)
        vehicle_id = self.browse(cr, uid, id, context=context).wagon_id
        data = {'value': value, 'date': date, 'vehicle_id': vehicle_id.id}
        odometer_id = self.pool.get('fleet.vehicle.odometer').create(
            cr, uid, data, context=context)
        return self.write(cr, uid, id, {'wagon_final_odometer_id': odometer_id}, context=context)

    def _get_distance(self, cr, uid, ids, fields, arg, context):
        res = dict.fromkeys(ids, False)
        for record in self.browse(cr, uid, ids, context=context):
            if record.initial_odometer and record.final_odometer:
                res[record.id] = record.final_odometer - \
                    record.initial_odometer
        return res

    def _get_amounts(self, cr, uid, ids, fields, arg, context):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            driver_total = False
            if record.driver_unit_price and record.distance:
                driver_total = record.driver_unit_price * record.distance
            res[record.id] = {
                'driver_total': driver_total,
            }
        return res

    def _get_fuel_data(self, cr, uid, ids, fields, arg, context):
        res = {}
        expense_obj = self.pool['logistic.waybill_expense']

        for record in self.browse(cr, uid, ids, context=context):
            charged_liters = 0.0
            fuel_charge_ids = expense_obj.search(cr, uid, [(
                'waybill_id', '=', record.id), ('product_id.is_fuel', '=', True)], context=context)
            for fuel_charge in expense_obj.browse(cr, uid, fuel_charge_ids, context=context):
                charged_liters += fuel_charge.product_uom_qty
            consumed_liters = record.initial_liters + \
                charged_liters - record.final_liters
            if record.distance != 0:
                consumption = consumed_liters / record.distance
            else:
                consumption = 0
            res[record.id] = {
                'charged_liters': charged_liters,
                'consumed_liters': consumed_liters,
                'consumption': consumption,
                'consumption_copy': consumption,
            }
        return res

    def _get_total_exp(self, cr, uid, ids, context=None):
        result = []
        for expense in self.pool.get('logistic.waybill_expense').browse(cr, uid, ids, context=context):
            if expense.product_uom_qty:
                result.append(expense.waybill_id.id)
        return result

    charged_liters = fields.Float(
        string='Charged', compute='_get_fuel_data', multi="fuel_data")
    consumed_liters = fields.Float(
        string='Consumed', compute='_get_fuel_data', multi="fuel_data")
    consumption = fields.Float(
        string='Consumption (l/km)', compute='_get_fuel_data', multi="fuel_data")
    consumption_copy = fields.Float(
        string='Consumption (l/km)',
        compute='_get_fuel_data',
        multi="fuel_data", store=True, group_operator="avg")
        # store={
        #     'logistic.waybill': (
        #         lambda self, cr, uid, ids, c={}: ids,
        #         ['consumption', 'initial_liters', 'final_liters', 'waybill_expense_ids', 'state', 'initial_odometer', 'final_odometer'],
        #         10),
        #     'logistic.waybill_expense': (
        #         _get_total_exp,
        #         ['product_uom_qty'],
        #         10)}, group_operator="avg")
    initial_odometer_id = fields.Many2one(
        'fleet.vehicle.odometer', 'Initial Odometer',
        help='Odometer measure of the vehicle at the moment of this log',
        readonly=True, states={'active': [('readonly', False)]})
    initial_odometer = fields.Float(
        fnct_inv=_set_initial_odometer,
        compute='_get_initial_odometer',
        string='Initial Odometer',
        readonly=True, states={'active': [('readonly', False)]})
    final_odometer_id = fields.Many2one(
        'fleet.vehicle.odometer', 'Final Odometer',
        help='Odometer measure of the vehicle at the moment of this log',
        readonly=True, states={'active': [('readonly', False)]})
    final_odometer = fields.function(
        fnct_inv=_set_final_odometer,
        compute='_get_final_odometer',
        string='Final Odometer',
        readonly=True, states={'active': [('readonly', False)]})
    distance = fields.Float(
        compute='_get_distance', string='Distance', store=True)
    driver_total = fields.Float(
        compute='_get_amounts', string='Driver Total', multi="_get_amounts")
    wagon_initial_odometer_id = fields.Many2one(
        'fleet.vehicle.odometer', 'Initial Odometer',
        help='Odometer measure of the vehicle at the moment of this log',
        readonly=True, states={'active': [('readonly', False)]})
    wagon_initial_odometer = fields.Float(
        fnct_inv=_set_wagon_initial_odometer,
        compute='_get_wagon_initial_odometer',
        string='Initial Odometer', readonly=True,
        states={'active': [('readonly', False)]})
    wagon_final_odometer_id = fields.Many2one(
        'fleet.vehicle.odometer', 'Final Odometer',
        help='Odometer measure of the vehicle at the moment of this log',
        readonly=True, states={'active': [('readonly', False)]})
    wagon_final_odometer = fields.Float(
        fnct_inv=_set_wagon_final_odometer,
        compute='_get_wagon_final_odometer',
        string='Final Odometer', readonly=True,
        states={'active': [('readonly', False)]})
    tractor_status = fields.Char(
        related='tractor_id.requirement_state', string='Tractor Status')
    wagon_status = fields.Char(
        related='wagon_id.requirement_state', string='Wagon Status')
    driver_status = fields.Char(
        related='driver_id.requirement_state', string='Driver Status')

    def on_change_tractor_final_odometer(self, cr, uid, ids, initial_odometer, final_odometer, wagon_initial_odometer, context=None):
        v = {}
        if initial_odometer and final_odometer and wagon_initial_odometer:
            v['wagon_final_odometer'] = final_odometer - \
                initial_odometer + wagon_initial_odometer
        return {'value': v}

    def on_change_wagon(self, cr, uid, ids, wagon_id, context=None):
        v = {}
        if wagon_id:
            wagon = self.pool.get('fleet.vehicle').browse(
                cr, uid, wagon_id, context=context)
            v['wagon_initial_odometer'] = wagon.odometer
        else:
            v['wagon_initial_odometer'] = False
        return {'value': v}

    def on_change_driver(self, cr, uid, ids, driver_id, context=None):
        v = {}
        if driver_id:
            driver = self.pool.get('res.partner').browse(
                cr, uid, driver_id, context=context)
            v['driver_product_id'] = driver.driver_product_id.id
        else:
            v['driver_product_id'] = False
        return {'value': v}

    def on_change_product(self, cr, uid, ids, product_id, context=None):
        v = {}
        if product_id:
            product = self.pool.get('product.product').browse(
                cr, uid, product_id, context=context)
            v['driver_unit_price'] = product.list_price
        else:
            v['driver_unit_price'] = False
        return {'value': v}

    def on_change_tractor(self, cr, uid, ids, tractor_id, context=None):
        v = {}
        if tractor_id:
            vehicle = self.pool.get('fleet.vehicle').browse(
                cr, uid, tractor_id, context=context)
            v['initial_odometer'] = vehicle.odometer
            if vehicle.wagon_id.id:
                v['wagon_id'] = vehicle.wagon_id.id
            else:
                v['wagon_id'] = False
                v['wagon_initial_odometer'] = False
            if vehicle.driver_id.id:
                v['driver_id'] = vehicle.driver_id.id
            else:
                v['driver_id'] = False
        else:
            v['initial_odometer'] = False
            v['wagon_initial_odometer'] = False
            v['wagon_id'] = False
            v['driver_id'] = False
        return {'value': v}

    def create(self, cr, uid, vals, context=None):
        if vals.get('name', '/') == '/':
            vals['name'] = self.pool.get('ir.sequence').get(
                cr, uid, 'logistic.waybill') or '/'
        return super(waybill, self).create(cr, uid, vals, context=context)

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'date': fields.date.context_today(self, cr, uid, context=context),
            'travel_ids': [],
            'waybill_expense_ids': [],
            'initial_odometer_id': False,
            'initial_odometer': self.browse(cr, uid, id, context=context).tractor_id.odometer,
            'final_odometer_id': False,
            'wagon_initial_odometer_id': False,
            'wagon_initial_odometer': self.browse(cr, uid, id, context=context).wagon_id.odometer,
            'wagon_final_odometer_id': False,
            'name': self.pool.get('ir.sequence').get(cr, uid, 'logistic.waybill'),
        })
        return super(waybill, self).copy(cr, uid, id, default, context=context)

    def check_closure(self, cr, uid, ids, context=None):
        travel_obj = self.pool['logistic.travel']
        for record in self.browse(cr, uid, ids, context=context):
            if not record.final_odometer or record.initial_odometer >= record.final_odometer:
                raise Warning(
                    _('Error!'), _('Tractor Final odometer must be greater than initial odometer!'))
            if not record.wagon_final_odometer or record.wagon_initial_odometer >= record.wagon_final_odometer:
                raise Warning(
                    _('Error!'), _('Wagon Final odometer must be greater than initial odometer!'))
            if not record.date_start:
                travel_ids = travel_obj.search(
                    cr, uid, [('waybill_id', '=', record.id)], order='from_date', context=context)
                if travel_ids and not record.date_start:
                    date_start = travel_obj.browse(
                        cr, uid, travel_ids[0], context=context).from_date
                    self.write(
                        cr, uid, [record.id], {'date_start': date_start}, context=context)
            if not record.date_finish:
                travel_ids = travel_obj.search(
                    cr, uid, [('waybill_id', '=', record.id)], order='to_date desc', context=context)
                if travel_ids and not record.date_finish:
                    date_finish = travel_obj.browse(
                        cr, uid, travel_ids[0], context=context).to_date
                    self.write(
                        cr, uid, [record.id], {'date_finish': date_finish}, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
