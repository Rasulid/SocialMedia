import uvicorn
from api.core.config import DB_NAME, DB_PORT, DB_USER, DB_PASS, DB_HOST

if __name__ == '__main__':
    uvicorn.run("api.main:app", host='0.0.0.0', port=8000, reload=True)
