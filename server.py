import json

from aiohttp import web
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.exc import IntegrityError

router = web.RouteTableDef()
app = web.Application()

PG_DSN = "postgresql+asyncpg://app:secret@127.0.0.1:5432/app"
engine = create_async_engine(PG_DSN)
Base = declarative_base()

class HTTPError(web.HTTPException):
    def __init__(self, *, headers=None, reason=None, body=None, message=None):
        json_response = json.dumps({'error': message})
        super().__init__(
            headers=headers, 
            reason=reason, 
            body=body, 
            text=json_response, 
            content_type='application/json',
        )

class BadRequest(HTTPError):
    status_code = 400

class NotFound(HTTPError):
    status_code = 400

class Advert(Base):
    __tablename__ = "Advert"

    id = Column(Integer, primary_key=True)
    header = Column(String(64), index=True, unique=True, nullable=False)
    description = Column(String(128))
    create_date = Column(DateTime, server_default=func.now())
    owner = Column(String(128))

async def get_advert(advert_id: int, session) -> Advert:
    advert = await session.get(Advert, advert_id)
    if not advert:
        raise NotFound(message='Advert not found')
    return advert

class AdvertView(web.View):

    async def get(self):
        advert_id = int(self.request.match_info['advert_id'])
        async with app.async_session_maker() as session:
            advert = await get_advert(advert_id=advert_id, session=session)
            return web.json_response({
                'id': advert.id,
                'header': advert.header,
                'description': advert.description,
                'create_date': int(advert.create_date.timestamp()),
                'owner': advert.owner,
                })

    async def post(self):
        advert_data = await self.request.json()
        new_advert = Advert(**advert_data)
        async with app.async_session_maker() as session:
            session.add(new_advert)
            try:
                await session.commit()
                return web.json_response({'id': new_advert.id})
            except IntegrityError as error:
                raise BadRequest(message='advert already exists')

    async def patch(self):
        advert_id = int(self.request.match_info['advert_id'])
        advert_data = await self.request.json()
        async with app.async_session_maker() as session:
            advert = await get_advert(advert_id=advert_id, session=session)
            for column, value in advert_data.items():
                setattr(advert, column, value)
            session.add(advert)
            await session.commit()
            advert = await session.get(Advert, advert_id)
            return web.json_response({
                'id': advert.id,
                'header': advert.header,
                'description': advert.description,
                'create_date': int(advert.create_date.timestamp()),
                'owner': advert.owner,
                })

    async def delete(self):
        advert_id = int(self.request.match_info['advert_id'])
        async with app.async_session_maker() as session:
            advert = await get_advert(advert_id=advert_id, session=session)
            await session.delete(advert)
            await session.commit()
            return web.json_response({'status': 'success'})

async def init_orm(app: web.Application):
    print('App has just run')
    async with engine.begin() as db_conn:
        await db_conn.run_sync(Base.metadata.create_all)
        async_session_maker = sessionmaker(
            engine, 
            expire_on_commit=False,
            class_=AsyncSession,
            )
        app.async_session_maker = async_session_maker
        yield
    print('App has just stopped')

app.cleanup_ctx.append(init_orm)
app.add_routes([web.get('/adverts/{advert_id:\d+}', AdvertView)])
app.add_routes([web.post('/adverts/', AdvertView)])
app.add_routes([web.patch('/adverts/{advert_id:\d+}', AdvertView)])
app.add_routes([web.delete('/adverts/{advert_id:\d+}', AdvertView)])
web.run_app(app)