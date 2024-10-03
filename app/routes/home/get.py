from fastapi import APIRouter


home_route = APIRouter(tags=['Home'])


@home_route.get('/')
async def root():
    return 'You are awesome!'

@home_route.get('/test')
async def test():
    return {'message': 'success'}