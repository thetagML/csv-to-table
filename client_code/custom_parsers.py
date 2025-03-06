import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import datetime

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:
#
#    from . import Module1
#
#    Module1.say_hello()
#

class datetime_preset():
  def __init__(self):
    self.custom_format = None
    

  def __call__(self, datetime_string=None):
    if datetime_string is None:
      return self
    if self.custom_format is None:
      raise ValueError("No Format String Set.")
    return datetime.datetime.strptime(datetime_string, self.custom_format)
  

class date_preset():
  def __init__(self):
    self.custom_format = None
    

  def __call__(self, date_string=None):
    if date_string is None:
      return self
    if self.custom_format is None:
      raise ValueError("No Format String Set.")
    return datetime.datetime.strptime(date_string, self.custom_format).date()
  
