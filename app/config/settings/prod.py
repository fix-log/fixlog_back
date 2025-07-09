from .base import *

from dotenv import load_dotenv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env.prod") # env 환경 분리 설정

DEBUG = False
ENVIRONMENT = "production"
