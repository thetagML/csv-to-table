from ._anvil_designer import header_selectionTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json
import datetime
from ..custom_parsers import datetime_preset, date_preset

class header_selection(header_selectionTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.has_headers = properties['has_headers']
    if self.has_headers:
      self.parse_data = {k:str for k in properties['header_list']} 
    else:
      self.parse_data = {k:str for k in range(len(properties['header_list']))}


    self.outer_group = FlowPanel()
    self.header_textboxes = []
    for k, header in enumerate(properties['header_list']):
      #group_select = ColumnPanel(role='card')
      group_select = FlowPanel(role='card',width=250)
      #group_select = LinearPanel(role='card')
      if not self.has_headers:
        header_textbox = TextBox(
                                  tag=k,
                                  text=f"Column_{k}",
                                  tooltip=f"Assign a new Name for 'Column_{k}' by changing it here.",
                                  width=225
                                    )
        self.header_textboxes.append(header_textbox)
        group_select.add_component(header_textbox)
      group_select.add_component(Label(text=header,width=225))
      #drop_down = deepcopy(self.drop_down_column_type)
      #drop_down.tag = header
      group_select.add_component(self.make_dropdown(header) if self.has_headers else self.make_dropdown(k) )
      self.outer_group.add_component(group_select)
    self.add_component(self.outer_group)
    self.map_to_class = {
                          'str' : str,
                          'int' :  int,
                          'float' :  float,
                          'bool' :  bool,
                          'datetime.date' : date_preset,
                          'datetime.datetime' : datetime_preset,
                          'json.loads' : json.loads,
                          'None' : None
                            }
    
  
    
    
  def make_dropdown(self, column_name):
    drop_down = DropDown(
                    items=[
                            'Text - (str)',
                            'Number - (int)',
                            'Number - (float)',
                            'True/False - (bool)',
                            'Date - (datetime.date)',
                            'Date and Time - (datetime.datetime)',
                            'Simple Object - (json.loads)',
                            'Skip/Do not Import - (None)'
                              ],
                    tag=column_name,
                    tooltip=f"Please select a Column type for the '{column_name}' column.",
                    width=200,
                    )
    drop_down.add_event_handler('change', self.drop_down_change_event)
    
    return drop_down

  def drop_down_change_event(self, **event_args):
    drop_down = event_args['sender']

    selection = drop_down.selected_value[drop_down.selected_value.index("(")+1:drop_down.selected_value.index(")")]
    self.parse_data[drop_down.tag] = self.map_to_class[selection]
    #print(self.parse_data)
    
    default_custom_format = {
                              'datetime.datetime': "%Y-%m-%dA%H:%M:%S.%f%z", #anvil default "%Y-%m-%dA%H:%M:%S.%f%z"
                              'datetime.date': "%Y-%m-%d", #anvil default "%Y-%m-%d"
                                }
    
    #custom parser selections
    if selection  in ('datetime.datetime','datetime.date') :
      # apply to 'date' style
      # create a new instance object of custom class
      
      self.parse_data[drop_down.tag] = self.parse_data[drop_down.tag]()
      custom_format = default_custom_format[selection]
      
      self.parse_data[drop_down.tag].custom_format = custom_format
      drop_down.parent.add_component(self.create_custom_format_input(drop_down.tag, selection, custom_format))




  def create_custom_format_input(self, column_name, custom_type, placeholder=None):
    
    if custom_type in ('datetime.datetime','datetime.date'):
      # apply to 'date' style
      component = TextBox(
                            placeholder=placeholder if placeholder is not None else "",
                            tag=column_name,
                            tooltip=f"'{placeholder}' is the {custom_type} format used by an anvil csv export" if placeholder is not None else "Please enter a format for the parser."
                              )
      component.set_event_handler('lost_focus', self.custom_input_selection_change)
    
    return component
  
  
  def custom_input_selection_change(self, **event_args):
    custom_sender = event_args['sender']

    self.parse_data[custom_sender.tag].custom_format = custom_sender.text

  
  def button_finish_selection_click(self, **event_args):
    if self.has_headers:
      self.raise_event("x-close-alert", value=[(k,v) for k,v in self.parse_data.items()])
    else:
      self.raise_event("x-close-alert", value=[(self.header_textboxes[int(k)].text,v) for k,v in self.parse_data.items()])

    
  

