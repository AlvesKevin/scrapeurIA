from typing import Optional, Dict, List
from datetime import datetime, timedelta
import random
from app.database.mongodb import get_database
from app.core.config import settings

class ProxyManager:
    def __init__(self):
        self.db = get_database()
        
    async def get_proxy(self) -> Optional[Dict[str, str]]:
        """Récupère un proxy disponible avec la meilleure performance"""
        if not settings.USE_PROXY:
            return None
            
        proxy = await self.db.proxy_pool.find_one({
            "status": "active",
            "last_used": {
                "$lt": datetime.utcnow() - timedelta(seconds=settings.PROXY_ROTATION_INTERVAL)
            }
        }, sort=[("success_rate", -1)])
        
        if proxy:
            await self.db.proxy_pool.update_one(
                {"_id": proxy["_id"]},
                {
                    "$set": {
                        "last_used": datetime.utcnow()
                    }
                }
            )
            return {
                "http": f"{proxy['protocol']}://{proxy['ip']}:{proxy['port']}",
                "https": f"{proxy['protocol']}://{proxy['ip']}:{proxy['port']}"
            }
        return None
        
    async def update_proxy_status(self, proxy_url: str, success: bool, response_time: float):
        """Met à jour les statistiques du proxy"""
        protocol, address = proxy_url.split("://")
        ip, port = address.split(":")
        
        update = {
            "$inc": {"total_requests": 1},
            "$set": {"last_used": datetime.utcnow()}
        }
        
        if success:
            update["$inc"]["successful_requests"] = 1
            update["$set"]["last_success"] = datetime.utcnow()
        else:
            update["$inc"]["failed_requests"] = 1
            
        await self.db.proxy_pool.update_one(
            {"ip": ip, "port": int(port)},
            {
                **update,
                "$set": {
                    "response_time": response_time,
                    "success_rate": await self._calculate_success_rate(ip, port)
                }
            }
        )
        
    async def _calculate_success_rate(self, ip: str, port: int) -> float:
        """Calcule le taux de succès d'un proxy"""
        proxy = await self.db.proxy_pool.find_one({"ip": ip, "port": port})
        if not proxy:
            return 0.0
            
        total = proxy.get("total_requests", 0)
        if total == 0:
            return 0.0
            
        successful = proxy.get("successful_requests", 0)
        return (successful / total) * 100 