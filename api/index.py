from vercel_fastapi import VercelAPIHandler
from app.main import app

handler = VercelAPIHandler(app)
