# resources/customer.py
from app.utils.response import APIResponse
import uuid
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from app.models.customer import Customer


class GuestIdResource(Resource):
    def get(self):
        """Generate temporary guest unique identifier"""
        guest_id = str(uuid.uuid4())
        return APIResponse.success({
            'guest_id': guest_id
        })


class CustomerDetailResource(Resource):
    @jwt_required()
    def get(self, customer_id):
        """Get customer detailed information"""
        customer = Customer.query.get_or_404(customer_id)
        return APIResponse.success({
            'id': customer.id,
            'email': customer.email,
            'level': customer.level,
            'created_at': customer.created_at.isoformat(),
            'storage': customer.storage
        })
