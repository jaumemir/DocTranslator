# resources/prompt.py
from datetime import date
from flask import request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from app import db
from app.models import Customer
from app.models.prompt import Prompt, PromptFav
from app.utils.response import APIResponse



# Get prompt list
class MyPromptListResource(Resource):
    @jwt_required()
    def get(self):
        """Get my prompt list"""
        # Query all data directly (no query parameter parsing)
        query = Prompt.query.filter_by(customer_id=get_jwt_identity(), deleted_flag='N')
        prompts = [{
            'id': p.id,
            'title': p.title,
            'content': p.content,  # [:100] + '...' if len(p.content) > 100 else p.content
            'share_flag': p.share_flag,
            'created_at': p.created_at.isoformat() if p.created_at else None
        } for p in query.all()]

        # Return result
        return APIResponse.success({
            'data': prompts,
            'total': len(prompts)
        })


# Get shared prompt list
class SharedPromptListResource(Resource):
    def get(self):
        """Get shared prompt list"""
        # Parse parameters from query string
        parser = reqparse.RequestParser()
        parser.add_argument('porder', type=str, default='latest', location='args')  # Sort parameter
        args = parser.parse_args()

        # Query shared prompts
        query = db.session.query(
            Prompt,  # Get complete Prompt information
            func.count(PromptFav.id).label('fav_count'),  # Dynamically calculate favorite count
            Customer.email.label('customer_email')  # Get user's email
        ).outerjoin(
            PromptFav, Prompt.id == PromptFav.prompt_id
        ).outerjoin(
            Customer, Prompt.customer_id == Customer.id  # Associate Customer via customer_id
        ).filter(
            Prompt.share_flag == 'Y',
            Prompt.deleted_flag == 'N'
        ).group_by(
            Prompt.id
        )

        # Sort based on porder parameter
        if args['porder'] == 'latest':
            query = query.order_by(Prompt.created_at.desc())  # Sort by latest
        elif args['porder'] == 'added':
            query = query.order_by(Prompt.added_count.desc())  # Sort by add count
        elif args['porder'] == 'fav':
            query = query.order_by(func.count(PromptFav.id).desc())  # Sort by favorite count

        # Get all results directly
        results = query.all()

        prompts = [{
            'id': prompt.id,
            'title': prompt.title,
            'content': prompt.content,  # Return complete prompt content
            'email': customer_email if customer_email else '匿名用户',  # Use email from query result
            'share_flag': prompt.share_flag,
            'added_count': prompt.added_count,
            'created_at': prompt.created_at.strftime('%Y-%m-%d') if prompt.created_at else None,
            'updated_at': prompt.updated_at.strftime('%Y-%m-%d') if prompt.updated_at else None,
            'fav_count': fav_count
        } for prompt, fav_count, customer_email in results]

        # Return result
        return APIResponse.success({
            'data': prompts,
            'total': len(prompts)
        })


# Edit prompt content
class EditPromptResource(Resource):
    @jwt_required()
    def post(self, id):
        """Edit prompt content"""
        prompt = Prompt.query.filter_by(
            id=id,
            customer_id=get_jwt_identity(),
            deleted_flag='N'
        ).first_or_404()

        data = request.form
        if 'title' in data:
            if len(data['title']) > 255:
                return APIResponse.error('标题过长', 400)
            prompt.title = data['title']

        if 'content' in data:
            if len(data['content']) > 5000:
                return APIResponse.error('内容超过5000字符限制', 400)
            prompt.content = data['content']

        db.session.commit()
        return APIResponse.success(message='提示语更新成功')


# Update share status
class SharePromptResource(Resource):
    @jwt_required()
    def post(self, id):
        """
        Update share status
        :param id: prompt ID (path parameter)
        """
        # Query prompt by id and current user
        prompt = Prompt.query.filter_by(
            id=id,
            customer_id=get_jwt_identity(),
            deleted_flag='N'
        ).first_or_404()

        # Get share_flag from request body
        data = request.form
        if not data or 'share_flag' not in data or data['share_flag'] not in ['Y', 'N']:
            return APIResponse.error('无效的共享状态参数', 400)

        # Update share status
        prompt.share_flag = data['share_flag']
        db.session.commit()

        return APIResponse.success(message='共享状态已更新')


# Copy to my prompt library
class CopyPromptResource(Resource):
    @jwt_required()
    def post(self, id):
        """Copy to my prompt library"""
        original = Prompt.query.filter_by(
            id=id,
            share_flag='Y',
            deleted_flag='N'
        ).first_or_404()

        new_prompt = Prompt(
            title=f"{original.title} (副本)",
            content=original.content,
            customer_id=get_jwt_identity(),
            share_flag='N',
            added_count=0
        )
        db.session.add(new_prompt)
        db.session.commit()
        return APIResponse.success({
            'new_id': new_prompt.id,
            'message': '复制成功'
        })


# Favorite/unfavorite
class FavoritePromptResource(Resource):
    @jwt_required()
    def post(self, id):
        """Favorite/unfavorite"""
        prompt = Prompt.query.get_or_404(id)
        customer_id = get_jwt_identity()

        fav = PromptFav.query.filter_by(
            prompt_id=id,
            customer_id=customer_id
        ).first()

        if fav:
            db.session.delete(fav)
            action = 'unfavorite'
        else:
            new_fav = PromptFav(
                prompt_id=id,
                customer_id=customer_id
            )
            db.session.add(new_fav)
            action = 'favorite'

        prompt.added_count = prompt.added_count + (1 if not fav else -1)
        db.session.commit()
        return APIResponse.success(message=f'{action}成功')


# Create new prompt

class CreatePromptResource(Resource):
    @jwt_required()
    def post(self):
        """Create new prompt"""
        data = request.form
        required_fields = ['title', 'content']
        if not all(field in data for field in required_fields):
            return APIResponse.error('缺少必要参数', 400)

        if len(data['title']) > 255:
            return APIResponse.error('标题过长', 400)
        if len(data['content']) > 5000:
            return APIResponse.error('内容超过5000字符限制', 400)

        # Automatically set created_at to current time when creating
        prompt = Prompt(
            title=data['title'],
            content=data['content'],
            customer_id=get_jwt_identity(),
            share_flag=data.get('share_flag', 'N'),
            created_at=date.today()
        )
        db.session.add(prompt)
        db.session.commit()
        return APIResponse.success({
            'id': prompt.id,
            'message': '创建成功'
        })


# Delete prompt
class DeletePromptResource(Resource):
    @jwt_required()
    def delete(self, id):
        """Delete prompt"""
        prompt = Prompt.query.filter_by(
            id=id,
            customer_id=get_jwt_identity()
        ).first_or_404()

        prompt.deleted_flag = 'Y'
        db.session.commit()
        return APIResponse.success(message='删除成功')
