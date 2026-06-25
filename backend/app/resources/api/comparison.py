# resources/comparison.py
import zipfile
from io import BytesIO
import pandas as pd
import pytz
from flask import request, current_app, send_file
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Customer
from app.models.comparison import Comparison, ComparisonFav
from app.utils.response import APIResponse
from sqlalchemy import func
from datetime import datetime



class MyComparisonListResource(Resource):
    @jwt_required()
    def get(self):
        """Get my terminology list"""
        # Query all data directly (no query parameter parsing)
        query = Comparison.query.filter_by(customer_id=get_jwt_identity())
        comparisons = [self._format_comparison(comparison) for comparison in query.all()]

        # Return result
        return APIResponse.success({
            'data': comparisons,
            'total': len(comparisons)
        })

    def _format_comparison(self, comparison):
        """Format terminology data"""
        # Parse content field
        content_list = []
        if comparison.content:
            for item in comparison.content.split('; '):
                if ':' in item:
                    origin, target = item.split(':', 1)
                    content_list.append({
                        'origin': origin.strip(),
                        'target': target.strip()
                    })

        # Return formatted data
        return {
            'id': comparison.id,
            'title': comparison.title,
            'origin_lang': comparison.origin_lang,
            'target_lang': comparison.target_lang,
            'share_flag': comparison.share_flag,
            'added_count': comparison.added_count,
            'content': content_list,  # 返回解析后的数组
            'customer_id': comparison.customer_id,
            'created_at': comparison.created_at.strftime(
                '%Y-%m-%d %H:%M') if comparison.created_at else None,  # Format time
            'updated_at': comparison.updated_at.strftime(
                '%Y-%m-%d %H:%M') if comparison.updated_at else None,  # Format time
            'deleted_flag': comparison.deleted_flag
        }


# Get shared terminology list
class SharedComparisonListResource(Resource):
    @jwt_required()
    def get(self):
        """Get shared terminology list"""
        # Parse parameters from query string
        parser = reqparse.RequestParser()
        parser.add_argument('order', type=str, default='latest', location='args')  # Only keep sort parameter
        args = parser.parse_args()

        # Query shared terminologies and join Customer table to get user email
        query = db.session.query(
            Comparison,
            func.count(ComparisonFav.id).label('fav_count'),
            Customer.email.label('customer_email')
        ).outerjoin(
            ComparisonFav, Comparison.id == ComparisonFav.comparison_id
        ).outerjoin(
            Customer, Comparison.customer_id == Customer.id
        ).filter(
            Comparison.share_flag == 'Y',
            Comparison.deleted_flag == 'N'
        ).group_by(
            Comparison.id
        )

        # Sort based on order parameter
        if args['order'] == 'latest':
            query = query.order_by(Comparison.created_at.desc())
        elif args['order'] == 'added':
            query = query.order_by(Comparison.added_count.desc())
        elif args['order'] == 'fav':
            query = query.order_by(func.count(ComparisonFav.id).desc())

        # Get all results directly
        results = query.all()

        comparisons = [{
            'id': comparison.id,
            'title': comparison.title,
            'origin_lang': comparison.origin_lang,
            'target_lang': comparison.target_lang,
            'content': self.parse_content(comparison.content),
            'email': customer_email if customer_email else '匿名用户',
            'added_count': comparison.added_count,
            'created_at': comparison.created_at.strftime('%Y-%m-%d %H:%M'),
            'faved': self.check_faved(comparison.id),
            'fav_count': fav_count
        } for comparison, fav_count, customer_email in results]

        # Return result
        return APIResponse.success({
            'data': comparisons,
            'total': len(comparisons)
        })



# Edit terminology list
class EditComparisonResource(Resource):
    @jwt_required()
    def post(self, id):
        """Edit terminology"""
        comparison = Comparison.query.filter_by(
            id=id,
            customer_id=get_jwt_identity()
        ).first_or_404()

        data = request.form
        if 'title' in data:
            comparison.title = data['title']
        if 'origin_lang' in data:
            comparison.origin_lang = data['origin_lang']
        if 'target_lang' in data:
            comparison.target_lang = data['target_lang']
        if 'share_flag' in data:
            comparison.share_flag = data['share_flag']
        if 'added_count' in data:
            try:
                comparison.added_count = int(data['added_count'])
            except ValueError:
                return APIResponse.error("无效的 added_count 格式", 400)

        # Update content
        content_list = []
        for key, value in data.items():
            if key.startswith('content[') and '][origin]' in key:
                # Extract index
                index = key.split('[')[1].split(']')[0]
                origin = value
                target = data.get(f'content[{index}][target]', '')
                content_list.append(f"{origin}: {target}")

        # Convert content_list to string
        content_str = '; '.join(content_list)
        comparison.content = content_str

        # Get timezone from application configuration
        timezone_str = current_app.config['TIMEZONE']
        timezone = pytz.timezone(timezone_str)

        # Update updated_at field
        comparison.updated_at = datetime.now(timezone)

        db.session.commit()
        return APIResponse.success(message='术语表更新成功')


# Update terminology share status
class ShareComparisonResource(Resource):
    @jwt_required()
    def post(self, id):
        """Update share status"""
        comparison = Comparison.query.filter_by(
            id=id,
            customer_id=get_jwt_identity()
        ).first_or_404()

        data = request.form
        if 'share_flag' not in data or data['share_flag'] not in ['Y', 'N']:
            return APIResponse.error('share_flag 参数无效', 400)

        comparison.share_flag = data['share_flag']
        db.session.commit()
        return APIResponse.success(message='共享状态已更新')


# Copy to my terminology library
class CopyComparisonResource(Resource):
    @jwt_required()
    def post(self, id):
        """Copy to my terminology library"""
        comparison = Comparison.query.filter_by(
            id=id,
            share_flag='Y'
        ).first_or_404()

        new_comparison = Comparison(
            title=f"{comparison.title} (副本)",
            content=comparison.content,
            origin_lang=comparison.origin_lang,
            target_lang=comparison.target_lang,
            customer_id=get_jwt_identity(),
            share_flag='N'
        )
        db.session.add(new_comparison)
        db.session.commit()
        return APIResponse.success({
            'new_id': new_comparison.id
        })


# Favorite/unfavorite
class FavoriteComparisonResource(Resource):
    @jwt_required()
    def post(self, id):
        """Favorite/unfavorite"""
        comparison = Comparison.query.filter_by(id=id).first_or_404()
        customer_id = get_jwt_identity()

        favorite = ComparisonFav.query.filter_by(
            comparison_id=id,
            customer_id=customer_id
        ).first()

        if favorite:
            db.session.delete(favorite)
            message = '已取消收藏'
        else:
            new_favorite = ComparisonFav(
                comparison_id=id,
                customer_id=customer_id
            )
            db.session.add(new_favorite)
            message = '已收藏'

        db.session.commit()
        return APIResponse.success(message=message)


# Create new terminology
class CreateComparisonResource(Resource):
    @jwt_required()
    def post(self):
        """Create new terminology"""
        data = request.form
        required_fields = ['title', 'share_flag', 'origin_lang', 'target_lang']
        if not all(field in data for field in required_fields):
            return APIResponse.error('缺少必要参数', 400)

        # Parse content parameter
        content_list = []
        for key, value in data.items():
            if key.startswith('content[') and '][origin]' in key:
                # Extract index
                index = key.split('[')[1].split(']')[0]
                origin = value
                target = data.get(f'content[{index}][target]', '')
                content_list.append(f"{origin}: {target}")

        # Convert content_list to string
        content_str = '; '.join(content_list)

        # Get timezone from application configuration
        timezone_str = current_app.config['TIMEZONE']
        timezone = pytz.timezone(timezone_str)


        # Get current time
        current_time = datetime.now(timezone)

        # Create terminology
        comparison = Comparison(
            title=data['title'],
            origin_lang=data['origin_lang'],
            target_lang=data['target_lang'],
            content=content_str,  # Insert converted content string
            customer_id=get_jwt_identity(),
            share_flag=data.get('share_flag', 'N'),
            created_at=current_time,  # Explicit assignment
            updated_at=current_time  # Explicit assignment
        )
        db.session.add(comparison)
        db.session.commit()
        return APIResponse.success({
            'id': comparison.id
        })


# Delete terminology
class DeleteComparisonResource(Resource):
    @jwt_required()
    def delete(self, id):
        """Delete terminology"""
        comparison = Comparison.query.filter_by(
            id=id,
            customer_id=get_jwt_identity()
        ).first_or_404()

        db.session.delete(comparison)
        db.session.commit()
        return APIResponse.success(message='删除成功')


# Download template file
class DownloadTemplateResource(Resource):
    def get(self):
        """Download template file"""
        from flask import send_file
        from io import BytesIO
        import pandas as pd

        # Create template file
        df = pd.DataFrame(columns=['源术语', '目标术语'])
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='术语表模板.xlsx'
        )


# Import terminology
class ImportComparisonResource(Resource):
    @jwt_required()
    def post(self):
        """
        Import Excel file
        """
        # Check if file was uploaded
        if 'file' not in request.files:
            return APIResponse.error('未选择文件', 400)
        file = request.files['file']

        try:
            # Read Excel file
            import pandas as pd
            df = pd.read_excel(file)

            # Check if file contains required columns
            if not {'源术语', '目标术语'}.issubset(df.columns):
                return APIResponse.error('文件格式不符合模板要求', 406)
            # Parse Excel file content
            content = ';'.join(
                [f"{row['源术语']}: {row['目标术语']}" for _, row in df.iterrows()])  # Separated by ': '
            # Create terminology
            comparison = Comparison(
                title='导入的术语表',
                origin_lang='未知',
                target_lang='未知',
                content=content,  # Use improved format
                customer_id=get_jwt_identity(),
                share_flag='N'
            )
            db.session.add(comparison)
            db.session.commit()

            # Return success response
            return APIResponse.success({
                'id': comparison.id
            })
        except Exception as e:
            # Catch and return error information
            return APIResponse.error(f"文件导入失败：{str(e)}", 500)


# Export single terminology
class ExportComparisonResource(Resource):
    @jwt_required()
    def get(self, id):
        """
        Export single terminology
        """
        # Get current user ID
        current_user_id = get_jwt_identity()

        # Query terminology
        comparison = Comparison.query.get_or_404(id)
        print(comparison.customer_id, current_user_id)
        # Check if terminology is shared or belongs to current user
        if comparison.share_flag == 'Y' or comparison.customer_id != int(current_user_id):
            return {'message': '术语表未共享或无权限访问', 'code': 403}, 403

        # Parse terminology content
        terms = [term.split(': ') for term in comparison.content.split(';')]  # Split by ': '
        df = pd.DataFrame(terms, columns=['源术语', '目标术语'])

        # Create Excel file
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)

        # Return file download response
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'{comparison.title}.xlsx'
        )




# Batch export all terminologies
class ExportAllComparisonsResource(Resource):
    @jwt_required()
    def get(self):
        """
        Batch export all terminologies
        """
        # Get current user ID
        current_user_id = get_jwt_identity()

        # Query all terminologies for current user
        comparisons = Comparison.query.filter_by(customer_id=current_user_id).all()

        # Create ZIP file
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            for comparison in comparisons:
                # Parse terminology content
                terms = [term.split(': ') for term in comparison.content.split(';')]  # Split by ': '
                df = pd.DataFrame(terms, columns=['源术语', '目标术语'])

                # Create Excel file
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)
                output.seek(0)

                # Add Excel file to ZIP
                zf.writestr(f"{comparison.title}.xlsx", output.getvalue())

        memory_file.seek(0)

        # Return ZIP file download response
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'术语表_{datetime.now().strftime("%Y%m%d")}.zip'
        )
