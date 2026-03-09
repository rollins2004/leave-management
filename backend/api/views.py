"""
All views use pymongo directly - no Django ORM.
MongoDB Atlas stores all users and leaves.
"""
import bcrypt
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .db_mongo import users_col, leaves_col
from .auth import make_token_pair, decode_refresh_token, MongoUser, MongoJWTAuthentication


# ─── Permission helpers ───────────────────────────────────────────────────────

class IsEmployer(permissions.BasePermission):
    message = "Only employer accounts can perform this action."

    def has_permission(self, request, view):
        return getattr(request.user, 'is_employer', False)


# ─── Auth Views ───────────────────────────────────────────────────────────────

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        role = data.get('role', 'employee')

        # Validation
        errors = {}
        if not username:
            errors['username'] = ['This field is required.']
        elif users_col().find_one({'username': username}):
            errors['username'] = ['A user with this username already exists.']

        if not email:
            errors['email'] = ['This field is required.']
        elif users_col().find_one({'email': email}):
            errors['email'] = ['A user with this email already exists.']

        if not password or len(password) < 6:
            errors['password'] = ['Password must be at least 6 characters.']

        if role not in ('employee', 'employer'):
            errors['role'] = ['Role must be employee or employer.']

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        # Hash password
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        doc = {
            'username': username,
            'email': email,
            'password': hashed,
            'first_name': first_name,
            'last_name': last_name,
            'role': role,
            'created_at': datetime.utcnow(),
        }
        result = users_col().insert_one(doc)
        doc['_id'] = result.inserted_id

        user = MongoUser(doc)
        access, refresh = make_token_pair(doc)

        return Response({
            'message': 'Registration successful',
            'access': access,
            'refresh': refresh,
            'user': user.to_dict(),
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        if not username or not password:
            return Response(
                {'non_field_errors': ['Username and password are required.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        doc = users_col().find_one({'username': username})
        if not doc or not bcrypt.checkpw(password.encode(), doc['password'].encode()):
            return Response(
                {'non_field_errors': ['Invalid username or password.']},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user = MongoUser(doc)
        access, refresh = make_token_pair(doc)

        return Response({
            'access': access,
            'refresh': refresh,
            'user': user.to_dict(),
        })


class TokenRefreshView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token required.'}, status=400)

        try:
            payload = decode_refresh_token(refresh_token)
        except Exception as e:
            return Response({'error': str(e)}, status=401)

        doc = users_col().find_one({'_id': ObjectId(payload['user_id'])})
        if not doc:
            return Response({'error': 'User not found.'}, status=401)

        access, new_refresh = make_token_pair(doc)
        return Response({'access': access, 'refresh': new_refresh})


# ─── Leave helpers ────────────────────────────────────────────────────────────

def serialize_leave(leave):
    """Convert a MongoDB leave document to a JSON-safe dict."""
    employee_id = leave.get('employee_id')
    employee_name = leave.get('employee_name', '')
    employee_username = leave.get('employee_username', '')

    return {
        'id': str(leave['_id']),
        'employee': str(employee_id) if employee_id else None,
        'employee_name': employee_name,
        'employee_username': employee_username,
        'leave_type': leave.get('leave_type'),
        'start_date': leave.get('start_date'),
        'end_date': leave.get('end_date'),
        'reason': leave.get('reason'),
        'status': leave.get('status', 'pending'),
        'comments': leave.get('comments', ''),
        'applied_on': leave.get('applied_on').isoformat() if leave.get('applied_on') else None,
        'updated_on': leave.get('updated_on').isoformat() if leave.get('updated_on') else None,
    }


# ─── Employee Views ───────────────────────────────────────────────────────────

class EmployeeLeaveListCreateView(APIView):
    authentication_classes = [MongoJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """List current employee's leaves."""
        leaves = list(leaves_col().find(
            {'employee_id': ObjectId(request.user.id)},
            sort=[('applied_on', -1)]
        ))
        return Response([serialize_leave(l) for l in leaves])

    def post(self, request):
        """Apply for leave."""
        data = request.data
        leave_type = data.get('leave_type', '').strip()
        start_date = data.get('start_date', '').strip()
        end_date = data.get('end_date', '').strip()
        reason = data.get('reason', '').strip()

        errors = {}
        valid_types = ('sick', 'casual', 'annual', 'other')
        if leave_type not in valid_types:
            errors['leave_type'] = [f'Must be one of: {", ".join(valid_types)}']
        if not start_date:
            errors['start_date'] = ['This field is required.']
        if not end_date:
            errors['end_date'] = ['This field is required.']
        if not reason:
            errors['reason'] = ['This field is required.']
        if start_date and end_date and end_date < start_date:
            errors['end_date'] = ['End date must be after start date.']

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        doc = {
            'employee_id': ObjectId(request.user.id),
            'employee_name': request.user.get_full_name(),
            'employee_username': request.user.username,
            'leave_type': leave_type,
            'start_date': start_date,
            'end_date': end_date,
            'reason': reason,
            'status': 'pending',
            'comments': '',
            'applied_on': datetime.utcnow(),
            'updated_on': datetime.utcnow(),
        }
        result = leaves_col().insert_one(doc)
        doc['_id'] = result.inserted_id

        return Response(serialize_leave(doc), status=status.HTTP_201_CREATED)


# ─── Employer Views ───────────────────────────────────────────────────────────

class EmployerLeaveListView(APIView):
    authentication_classes = [MongoJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsEmployer]

    def get(self, request):
        """List all employee leave requests, optional ?status= filter."""
        query = {}
        status_filter = request.query_params.get('status')
        if status_filter:
            query['status'] = status_filter

        leaves = list(leaves_col().find(query, sort=[('applied_on', -1)]))
        return Response([serialize_leave(l) for l in leaves])


class EmployerLeaveUpdateView(APIView):
    authentication_classes = [MongoJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsEmployer]

    def patch(self, request, pk):
        """Approve or reject a leave request."""
        try:
            leave_id = ObjectId(pk)
        except InvalidId:
            return Response({'error': 'Invalid leave ID.'}, status=400)

        leave = leaves_col().find_one({'_id': leave_id})
        if not leave:
            return Response({'error': 'Leave not found.'}, status=404)

        new_status = request.data.get('status')
        if new_status not in ('approved', 'rejected'):
            return Response({'error': 'Status must be approved or rejected.'}, status=400)

        update = {
            'status': new_status,
            'comments': request.data.get('comments', ''),
            'reviewed_by': request.user.username,
            'updated_on': datetime.utcnow(),
        }
        leaves_col().update_one({'_id': leave_id}, {'$set': update})
        updated = leaves_col().find_one({'_id': leave_id})
        return Response(serialize_leave(updated))
