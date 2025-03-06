from ._anvil_designer import csv_uploadTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..header_selection import header_selection

import anvil.tables
import anvil.js
import time
from math import floor
import datetime

class csv_upload(csv_uploadTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    # Created by @ianbuywise on the anvil forums for use by everyone with no restrictions or licence needed or credit due.
    # ymmv, use at your own risk, no guarantees, not maintained, this is free as in beer, etc.
    self.init_components(**properties)
    
    # Any code you write here will run when the form opens.
    self.parse_data = None
    self.abort_operation = False

  def file_loader_1_change(self, file, **event_args):
    
    try:  
      self.add_table = getattr(app_tables, self.text_box_table_name.text)
    except AttributeError as err:
      alert(err, "Unable to Access table")
      self.file_loader_1.clear()
      self.file_loader_1.enabled = False
      return
    
    if file:
      self.file_loader_1.enabled = False
      
      #self.process_file(file)
      getattr(self, RadioButton(group_name='radioGroup_processing').get_group_value())(file)
      
      self.file_loader_1.enabled = True
      

  def process_file_browser(self, csv_file):
    old_time = time.time()
    readlines = ( line for line in csv_file.get_bytes().split(b"\n"))
    
    #readlines = (x for x in anvil.js.call('$.csv.toArrays', csv_file.get_bytes().decode("utf-8")))
    #readlines = (x for x in anvil.js.call('$.csv.toArrays', csv_file.get_bytes()))
    self.print_to_console(f"File Loaded in {round(time.time() - old_time, 7)} seconds ")
    separator = self.drop_down_separator_select.selected_value
    separator = separator[separator.index("(")+1:separator.index(")")]
    
    
    #header_list = next(readlines)
    raw_header = next(readlines)
    header_list = anvil.js.call(
                                '$.csv.toArray',
                                raw_header.decode("utf-8"),
                                [separator,('"' if self.check_box_delimiter_quote.checked else "")]
                                  )
    self.parse_data = alert(
                              header_selection(
                                                header_list=header_list,
                                                has_headers=self.check_box_headers_toggle.checked
                                                  ),
                              large=True,
                              title='Select Column Types',
                              buttons=None
                                )
    
    
    print(self.parse_data)
    if not self.check_box_headers_toggle.checked :
      #ab = (gen for gen_concat in (a, b) for gen in gen_concat)
      # This repairs the generator, placing the first line back at the top
      readlines =  (gen for gen_concat in ((x for x in [raw_header] ), readlines) for gen in gen_concat)
    

    self.abort_operation = False
    self.button_abort_operation.enabled = True
    self.button_abort_operation2.enabled = True
    self.print_to_console("Working.", )
    with anvil.server.no_loading_indicator as l:
      for line_num, line in enumerate(readlines):
        #throw_away = anvil.js.call('$.csv.toArray', line.decode("utf-8"), )
        insert_row = anvil.js.call(
                              '$.csv.toArray',
                              line.decode("utf-8"),
                              [separator,('"' if self.check_box_delimiter_quote.checked else "")]
                                )
        #insert_row = line
        
        try:
          insert_row = {col:parse(v) for (col, parse), v in zip(self.parse_data, insert_row) if parse is not None}
        except Exception as err:
          print(err)
          insert_row = self.fallback_parse(insert_row)

        try:
          self.add_table.add_row(**insert_row)
        except Exception as err:
          if 'Permission denied:' in str(err):
            error_string = f"Error: ({err}):\n{insert_row}\n-------- Upload Failed, check table permissions. ----------"
            self.file_loader_1.enabled = False
            self.file_loader_1.clear()
            self.print_to_console(error_string)
            break
            
        
          self.print_to_console(f"Error in the following row ({err}):\n{insert_row}\n------------------")
          
        
        
        if line_num % 10 == 0 and line_num not in (0, 1000):
          self.print_to_console(".", newline=False)

          
          
          
        if line_num % 1000 == 0 and line_num != 0:
          time.sleep(.35)
          #self.print_to_console(insert_row)
          new_time = time.time()
          self.print_to_console(f"Parsed 1000 lines. ({line_num}) {round(new_time - old_time, 4)} seconds have elapsed. (approx. {round( line_num / ((new_time - old_time) / 60), 4)} rows per min.)")
          self.print_to_console("Working.", )
        if self.abort_operation:
          self.print_to_console("Abort Button was pressed. ")
          break

      self.button_abort_operation.enabled = False
      self.button_abort_operation2.enabled = False
      
    new_time = time.time()
    
    self.print_to_console(f"Total process time was {floor(( new_time - old_time ) / 60)} minutes and {round((new_time - old_time) % 60,4)} seconds.")
    return

  
  
  def process_file_server_module(self, csv_file):
    old_time = time.time()
    readlines = ( line for line in csv_file.get_bytes().split(b"\n"))
    
    #readlines = (x for x in anvil.js.call('$.csv.toArrays', csv_file.get_bytes().decode("utf-8")))
    #readlines = (x for x in anvil.js.call('$.csv.toArrays', csv_file.get_bytes()))
    self.print_to_console(f"File Loaded in {round(time.time() - old_time, 7)} seconds ")
    separator = self.drop_down_separator_select.selected_value
    separator = separator[separator.index("(")+1:separator.index(")")]
    
    if self.check_box_headers_toggle.checked  :
      #header_list = next(readlines)
      
      header_list = anvil.js.call(
                                  '$.csv.toArray',
                                  next(readlines).decode("utf-8"),
                                  [separator,('"' if self.check_box_delimiter_quote.checked else "")]
                                    )
      self.parse_data = alert(
                                header_selection(
                                                header_list=header_list,
                                                has_headers=self.check_box_headers_toggle.checked
                                                  ),
                                large=True,
                                title='Select Column Types',
                                buttons=None
                                  )
      print(self.parse_data)

    row_cashe = []
    max_lines = int(self.text_box_max_rows.text)
    self.abort_operation = False
    self.button_abort_operation.enabled = True
    self.button_abort_operation2.enabled = True
    self.print_to_console("Working.", )
    with anvil.server.no_loading_indicator as l:
      for line_num, line in enumerate(readlines):
        #throw_away = anvil.js.call('$.csv.toArray', line.decode("utf-8"), )
        insert_row = anvil.js.call(
                              '$.csv.toArray',
                              line.decode("utf-8"),
                              [separator,('"' if self.check_box_delimiter_quote.checked else "")]
                                )

        
        try:
          insert_row = {col:parse(v) for (col, parse), v in zip(self.parse_data, insert_row) if parse is not None}
        except Exception as err:
          print(err)
          insert_row = self.fallback_parse(insert_row)
        row_cashe.append(insert_row)
        if line_num % 10 == 0 and line_num not in (0, 1000):
          self.print_to_console(".", newline=False)
        if len(row_cashe) > int(self.text_box_max_rows.text):
          
          self.print_to_console(". Sending to server.", newline=False )
          server_old_time = time.time()
          if not self.send_rows_to_server(self.add_table, row_cashe):
            self.text_box_max_rows.text = int(int(self.text_box_max_rows.text) * (0.5 if not self.check_box_pause_automatic_increase.checked else 0.85))
            time.sleep(1)
            self.send_rows_to_server(self.add_table, row_cashe[:int(self.text_box_max_rows.text)])
            
            row_cashe = row_cashe[int(self.text_box_max_rows.text):]
            time.sleep(1)
            self.send_rows_to_server(self.add_table, row_cashe)
            
            row_cashe = []
          row_cashe = []
          if not self.check_box_pause_automatic_increase.checked:
            self.text_box_max_rows.text = int(int(self.text_box_max_rows.text) * 1.15)
          server_new_time = time.time()
          time.sleep(.35)
          self.print_to_console(f" (Server Time {round(server_new_time - server_old_time, 4)} seconds.)" , newline=False)
          self.print_to_console("Working." )
          
          if int(self.text_box_max_rows.text) < 15:
            # set lower bound
            self.text_box_max_rows.text = 15
          

        if line_num % 1000 == 0 and line_num != 0:
          new_time = time.time()
          self.print_to_console(f"Parsed 1000 lines. ({line_num}) {round(new_time - old_time, 4)} seconds have elapsed. (approx. {round( line_num / ((new_time - old_time) / 60), 4)} rows per min.)")
          self.print_to_console("Working.", )
        if self.abort_operation:
          self.print_to_console("Abort Button was pressed. ")
          break
          
      if row_cashe and not self.abort_operation:
        self.print_to_console(". Sending final rows to server.", newline=False )
        server_old_time = time.time()
        if not self.send_rows_to_server(self.add_table, row_cashe):
        
          self.text_box_max_rows.text = int(int(self.text_box_max_rows.text) * .5)
          time.sleep(1)
          self.send_rows_to_server(self.add_table, row_cashe[:int(self.text_box_max_rows.text)])
          
          row_cashe = row_cashe[int(self.text_box_max_rows.text):]
          time.sleep(1)
          self.send_rows_to_server(self.add_table, row_cashe)
          
          row_cashe = []
      self.button_abort_operation.enabled = False
      self.button_abort_operation2.enabled = False
      
    new_time = time.time()
    
    self.print_to_console(f"Total process time was {floor(( new_time - old_time ) / 60)} minutes and {round((new_time - old_time) % 60,4)} seconds.")
    return

  def send_rows_to_server(self, table, rows):
    try:
      result = anvil.server.call('send_rows_to_server', table, rows)
    except anvil.server.TimeoutError:
      self.print_to_console(f"Too many rows, reducing {len(rows)} row submission by {(50 if not self.check_box_pause_automatic_increase.checked else 15)}%")
      return False
    except anvil.server.ExecutionTerminatedError:
      self.print_to_console(f"Too many rows, reducing {len(rows)} row submission by {(50 if not self.check_box_pause_automatic_increase.checked else 15)}%")
      time.sleep(3)
      return False
    except Exception as err:
      if "AppOfflineError" in str(err):
        self.print_to_console("Major App Fault, sleeping for 30 seconds")
        time.sleep(30)
        if self.send_rows_to_server(table, rows):
          return True
        return False
      raise
      
    return True
 
  
  def fallback_parse(self, row_data):
    new_row_data = {}
    for (col, parse), val in zip(self.parse_data, row_data):
      if parse is None:
        continue
      try:
        new_row_data[col] = parse(val)
      except Exception as err:
        self.print_to_console(f"Skipped '{val}' in Column: {col} ! -- Reason: {err}")

        
    return new_row_data
  
  def text_box_table_name_change(self, **event_args):
    if not self.file_loader_1.enabled:
      self.file_loader_1.enabled = True


  def button_abort_operation_click(self, **event_args):
    self.button_abort_operation.enabled = False
    self.button_abort_operation2.enabled = False
    self.abort_operation = True

  def button_abort_operation2_click(self, **event_args):
    self.button_abort_operation.enabled = False
    self.button_abort_operation2.enabled = False
    self.abort_operation = True

  def radio_button_browser_clicked(self, **event_args):
    self.column_panel_browser_table_permissions.visible = True
    self.column_panel_server_settings.visible = False

  def radio_button_server_clicked(self, **event_args):
    self.column_panel_browser_table_permissions.visible = False
    self.column_panel_server_settings.visible = True

    
  def print_to_console(self, print_string, newline=True):
    if newline:
      self.text_area_print.text += f"\n{print_string}"
      return
    self.text_area_print.text += f"{print_string}"
    
