from .base import *

from dotenv import load_dotenv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env.local") # env 파일 설정

DEBUG = True
ENVIRONMENT = "local"