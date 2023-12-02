from aiohttp import web
from app.bot_src.API.database_api import get_awaiting_orders
import json


routes = web.RouteTableDef()



@routes.get('/get_awaiting_orders')
async def get_awaiting_orders_request(request):
    data = await get_awaiting_orders()
    data_json = json.dumps(data)
    return web.json_response(data_json, status=200)