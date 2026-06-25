# resources/admin/to_translate.py
import os
import zipfile
from datetime import datetime
from io import BytesIO
from flask import request, make_response, send_file
from flask_jwt_extended import jwt_required
from flask_restful import Resource, reqparse
from app import db
from app.models import Customer
from app.models.translate import Translate
from app.utils.response import APIResponse
from app.utils.validators import (
    validate_id_list
)


# Get translation record list
class AdminTranslateListResource(Resource):
    @jwt_required()
    def get(self):
        """Get translation record list"""
        # Get query parameters
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default=1, location='args')  # Page number, default 1
        parser.add_argument('limit', type=int, default=100, location='args')  # Items per page, default 100
        parser.add_argument('status', type=str, location='args')  # Status, optional
        parser.add_argument('keyword', type=str, location='args')  # Search keyword, optional
        args = parser.parse_args()

        # Build query conditions
        query = Translate.query.filter_by()

        # Check status filter condition
        if args['status']:
            valid_statuses = {'none', 'process', 'done', 'failed'}
            if args['status'] not in valid_statuses:
                return APIResponse.error(f"Invalid status value: {args['status']}"), 400
            query = query.filter_by(status=args['status'])
        # Check keyword filter condition
        if args['keyword']:
            # Fuzzy match origin_filename or customer_email
            query = query.join(Customer, Translate.customer_id == Customer.id).filter(
                (Translate.origin_filename.ilike(f"%{args['keyword']}%")) |
                (Customer.email.ilike(f"%{args['keyword']}%"))
            )
        # Execute paginated query
        pagination = query.paginate(page=args['page'], per_page=args['limit'], error_out=False)

        # Process each record
        data = []
        for t in pagination.items:
            # Calculate time spent (based on start_at and end_at)
            if t.start_at and t.end_at:
                spend_time = t.end_at - t.start_at
                spend_time_minutes = int(spend_time.total_seconds() // 60)
                spend_time_seconds = int(spend_time.total_seconds() % 60)
                spend_time_str = f"{spend_time_minutes}min{spend_time_seconds}s"
            else:
                spend_time_str = "--"

            # Get customer email (through Customer model association query)
            customer = Customer.query.get(t.customer_id)
            customer_email = customer.email if customer else "--"
            customer_no = customer.customer_no if customer.customer_no else t.customer_id
            # Format time fields
            start_at_str = t.start_at.strftime('%Y-%m-%d %H:%M:%S') if t.start_at else "--"
            end_at_str = t.end_at.strftime('%Y-%m-%d %H:%M:%S') if t.end_at else "--"

            # Build return data
            data.append({
                'id': t.id,
                'customer_no': customer_no,
                'customer_id': t.customer_id,  # Owning customer ID
                'customer_email': customer_email,  # Customer email
                'origin_filename': t.origin_filename,
                'status': t.status,
                'process': float(t.process) if t.process is not None else None,  # Convert to float
                'start_at': start_at_str,  # Start time
                'end_at': end_at_str,  # End time
                'spend_time': spend_time_str,  # Time spent
                'lang': t.lang,
                'target_filepath': t.target_filepath,
            'deleted_flag':t.deleted_flag
            })

        # Return response data
        return APIResponse.success({
            'data': data,
            'total': pagination.total,
            'current_page': pagination.page
        })


# Batch download multiple translation files
class AdminTranslateDownloadBatchResource(Resource):
    @jwt_required()
    def post(self):
        """Batch download multiple translation result files (admin interface)"""
        try:
            # Parse ids parameter from request body
            data = request.get_json()
            if not data or 'ids' not in data:
                return {"message": "Missing ids parameter"}, 400

            ids = data['ids']
            if not isinstance(ids, list):
                return {"message": "ids must be an array"}, 400

            # Query specified translation records
            records = Translate.query.filter(
                Translate.id.in_(ids),  # Filter specified IDs
                Translate.deleted_flag == 'N'  # Only download non-deleted records
            ).all()

            # Generate in-memory ZIP file
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                for record in records:
                    if record.target_filepath and os.path.exists(record.target_filepath):
                        # Add file to ZIP
                        zip_file.write(
                            record.target_filepath,
                            os.path.basename(record.target_filepath)
                        )

            # Reset buffer pointer
            zip_buffer.seek(0)

            # Return ZIP file
            return send_file(
                zip_buffer,
                mimetype='application/zip',
                as_attachment=True,
                download_name=f"translations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            )
        except Exception as e:
            return {"message": f"Server error: {str(e)}"}, 500


# Download single translation file
class AdminTranslateDownloadResource(Resource):
    # @jwt_required()
    def get(self, id):
        """Download single translation result file by ID"""
        # Query translation record
        translate = Translate.query.filter_by(
            id=id,
            # customer_id=get_jwt_identity()
        ).first_or_404()

        # Ensure file exists
        if not translate.target_filepath or not os.path.exists(translate.target_filepath):
            return APIResponse.error('File does not exist', 404)

        # Return file
        response = make_response(send_file(
            translate.target_filepath,
            as_attachment=True,
            download_name=os.path.basename(translate.target_filepath)
        ))

        # Disable cache
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'

        return response


# Delete single translation record
class AdminTranslateDeteleResource(Resource):
    @jwt_required()
    def delete(self, id):
        """Delete single translation record"""
        try:
            record = Translate.query.get_or_404(id)
            db.session.delete(record)
            db.session.commit()
            return APIResponse.success(message='Record deleted successfully')
        except Exception as e:
            db.session.rollback()
            return APIResponse.error('Deletion failed', 500)


class AdminTranslateBatchDeleteResource(Resource):
    def post(self):
        """Batch delete translation records"""
        try:
            ids = validate_id_list(request.json.get('ids'))
            if len(ids) > 100:
                return APIResponse.error('Maximum 100 records can be deleted at once', 400)

            Translate.query.filter(Translate.id.in_(ids)).delete()
            db.session.commit()
            return APIResponse.success(message=f'Successfully deleted {len(ids)} records')
        except APIResponse as e:
            return e
        except Exception as e:
            db.session.rollback()
            return APIResponse.error('Batch deletion failed', 500)


class AdminTranslateRestartResource(Resource):
    def post(self, id):
        """Restart translation task"""
        try:
            record = Translate.query.get_or_404(id)
            if record.status not in ['failed', 'done']:
                return APIResponse.error('Current status cannot be restarted', 400)

            record.status = 'none'
            record.start_at = None
            record.end_at = None
            record.failed_reason = None
            db.session.commit()
            return APIResponse.success(message='Task has been restarted')
        except Exception as e:
            db.session.rollback()
            return APIResponse.error('Restart failed', 500)


class AdminTranslateStatisticsResource(Resource):
    def get(self):
        """Get translation statistics"""
        try:
            total = Translate.query.count()
            done_count = Translate.query.filter_by(status='done').count()
            processing_count = Translate.query.filter_by(status='process').count()
            failed_count = Translate.query.filter_by(status='failed').count()

            return APIResponse.success({
                'total': total,
                'done_count': done_count,
                'processing_count': processing_count,
                'failed_count': failed_count
            })
        except Exception as e:
            return APIResponse.error('Failed to get statistics', 500)
