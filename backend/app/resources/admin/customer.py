# resources/admin/customer.py
from flask import request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required

from app import db
from app.models import Customer
from app.utils.auth_tools import hash_password
from app.utils.response import APIResponse


# Get customer list
class AdminCustomerListResource(Resource):
    @jwt_required()
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, required=False, location='args')  # Optional, default 1
        parser.add_argument('limit', type=int, required=False, location='args')  # Optional, default 10
        parser.add_argument('keyword', type=str, required=False, location='args')  # Optional, no default
        args = parser.parse_args()
        query = Customer.query
        if args['keyword']:
            query = query.filter(Customer.email.ilike(f"%{args['keyword']}%"))

        pagination = query.paginate(page=args['page'], per_page=args['limit'], error_out=False)
        customers = [c.to_dict() for c in pagination.items]
        return APIResponse.success({
            'data': customers,
            'total': pagination.total
        })


# Update customer status
class CustomerStatusResource(Resource):
    @jwt_required()
    def post(self, id):
        # Parse status parameter from request body
        parser = reqparse.RequestParser()
        parser.add_argument('status', type=str, required=True, choices=('enabled', 'disabled'),
                            help="Status must be 'enabled' or 'disabled'")
        args = parser.parse_args()

        # Query customer
        customer = Customer.query.get(id)
        if not customer:
            return APIResponse.error(message="Customer does not exist", code=404)

        # Update customer status
        customer.status = args['status']
        db.session.commit()  # Assuming db is your SQLAlchemy instance
        # Update customer status
        customer.status = args['status']
        print(f"Status before update: {customer.status}")  # Debug
        db.session.commit()
        print(f"Status after update: {customer.status}")  # Debug

        # Return updated customer info
        return APIResponse.success(data=customer.to_dict())


# Create new customer
class AdminCreateCustomerResource(Resource):
    @jwt_required()
    def put(self):
        data = request.json
        required_fields = ['email', 'password']  # 'name',
        if not all(field in data for field in required_fields):
            return APIResponse.error('Missing required parameters!', 400)

        if Customer.query.filter_by(email=data['email']).first():
            return APIResponse.error('Email already exists', 400)

        customer = Customer(
            # name=data['name'],
            email=data['email'],
            password=hash_password(data['password']),
            level=data.get('level', 'common')
        )
        db.session.add(customer)
        db.session.commit()
        return APIResponse.success({
            'customer_id': customer.id,
            'message': 'Customer created successfully'
        })


# Get customer information
class AdminCustomerDetailResource(Resource):
    @jwt_required()
    def get(self, id):
        customer = Customer.query.get_or_404(id)
        return APIResponse.success({
            'id': customer.id,
            'name': customer.name,
            'email': customer.email,
            'status': 'active' if customer.deleted_flag == 'N' else 'deleted',
            'level': customer.level,
            'created_at': customer.created_at.isoformat(),
            'storage': customer.storage,
            'total_storage': customer.total_storage,
        })


# Edit customer information
class AdminUpdateCustomerResource(Resource):
    @jwt_required()
    def post(self, id):
        customer = Customer.query.get_or_404(id)
        data = request.json

        if 'email' in data and Customer.query.filter(Customer.email == data['email'],Customer.id != id).first():
            return APIResponse.error('Email already in use', 400)

        if 'name' in data:
            customer.name = data['name']
        if 'email' in data:
            customer.email = data['email']
        if 'level' in data:
            customer.level = data['level']
        if 'add_storage' in data:
            customer.total_storage += int(data['add_storage']) * 1024 * 1024
        db.session.commit()
        return APIResponse.success(message='Customer information updated successfully')


# Delete customer
class AdminDeleteCustomerResource(Resource):
    @jwt_required()
    def delete(self, id):
        customer = Customer.query.get_or_404(id)
        customer.deleted_flag = 'Y'
        db.session.commit()
        return APIResponse.success(message='Customer deleted successfully')
