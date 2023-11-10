import os
from typing import Literal


PROJECT_PATH = os.path.abspath(f'{__file__}/../..')

WebmailServiceLiteral = Literal['gmail']
