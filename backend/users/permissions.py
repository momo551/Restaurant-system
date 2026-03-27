from rest_framework import permissions

from .models import ModulePermission

# Legacy mapping for compatibility with existing HasXXXAccess classes
LEGACY_MODULE_MAPPING = {
    'pos': 'pos',
    'tables': 'tables',
    'reports': 'reports',
    'dashboard': 'dashboard',
    'menu': 'menu',
    'delivery': 'delivery_monitor',
    'kitchen': 'orders',
    'staff': 'staff',
    'stock': 'ingredients',
}

class BaseRolePermission(permissions.BasePermission):
    """Base class for role-based permissions using MODULE_PERMISSIONS."""
    module_name = None

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        if request.user.role == 'owner':
            return True
        
        if not self.module_name:
            return False
            
        # Try to get dynamic permission from database
        module_key = LEGACY_MODULE_MAPPING.get(self.module_name, self.module_name)
        return ModulePermission.objects.filter(
            role=request.user.role, 
            module_key=module_key, 
            allowed=True
        ).exists()



class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'owner'

class IsOwnerOrSelf(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.role == 'owner' or obj == request.user

class HasPOSAccess(BaseRolePermission):
    module_name = 'pos'

class HasTablesAccess(BaseRolePermission):
    module_name = 'tables'

class HasReportsAccess(BaseRolePermission):
    module_name = 'reports'

class HasDashboardAccess(BaseRolePermission):
    module_name = 'dashboard'

class HasMenuAccess(BaseRolePermission):
    module_name = 'menu'

class HasDeliveryAccess(BaseRolePermission):
    module_name = 'delivery'

class HasKitchenAccess(BaseRolePermission):
    module_name = 'kitchen'

class HasStaffAccess(BaseRolePermission):
    module_name = 'staff'

class HasStockAccess(BaseRolePermission):
    module_name = 'stock'

class HasAuditLogAccess(BaseRolePermission):
    module_name = 'audit_log'

class HasPermissionsMatrixAccess(BaseRolePermission):
    module_name = 'permissions_matrix'

# Legacy support for old permission names to avoid breaking imports immediately
class IsManagerOrAbove(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['owner', 'manager', 'hall_manager']

class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['owner', 'manager', 'cashier', 'kitchen', 'delivery', 'hall_manager', 'hall_captain', 'hr']

class IsInventoryManager(permissions.BasePermission):
    """
    Allows access to inventory managers or the owner.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and
            (request.user.role in ['owner', 'inventory_manager'])
        )

