"""
FarmSense OS v1.0 - Multi-Tenant Cloud Server

Main server run
[truncated]
 tenant['limits']['max_fields']:
            raise TierLimitExceeded(
                f"Field limit reached: {tenant['limits']['max_fields']}"
            )
        
        tenant['fields'][field_id] = {
            'created': datetime.utcnow().isoformat(),
            'status': 'active',
            'sensors': [],
            'grid_resolution_m': tenant['limits']['virtual_grid_m']
        }
        
        await self._persist_tenant(tenant_id, tenant)
        return field_id
