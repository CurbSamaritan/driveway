import os

def get():
  if os.environ['SERVER_SOFTWARE'].startswith('Development'):
    from private import config_dev as cfg
  else:
     from private import config_prod as cfg
  return cfg.config


