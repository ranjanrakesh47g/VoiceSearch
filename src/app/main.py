import os
from dotenv import load_dotenv
from src.utils.logging_setup import setup_logging
import uvicorn
from src.app.api import app

load_dotenv()
setup_logging()


def main():
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT1", 7680)))


if __name__ == "__main__":
    main()
