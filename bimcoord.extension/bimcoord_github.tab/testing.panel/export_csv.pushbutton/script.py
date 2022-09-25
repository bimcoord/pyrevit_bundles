# -*- coding: utf-8 -*-
__title__ = 'Export\nCSV'
__doc__ = '''Define later in bundle.yaml'''
# Template
from Autodesk.Revit import DB
from rpw.ui import forms
import System

doc = __revit__.ActiveUIDocument.Document

# Checking document like family or project
if doc.IsFamilyDocument:
    owner_family_id = doc.OwnerFamily.Id
    family_size_table_manager = DB.FamilySizeTableManager.\
        GetFamilySizeTableManager(doc, owner_family_id) # Получение менеджера таблиц
    list_of_size_tables = list(family_size_table_manager.GetAllSizeTableNames())
    
    selected_size_table = forms.SelectFromList(
        '''Выберите csv-таблицу для экспорта''',
        list_of_size_tables
    )
    selected_size_table_name = selected_size_table
    selected_size_table = family_size_table_manager.GetSizeTable(selected_size_table_name)

    rows, columns = selected_size_table.NumberOfRows, selected_size_table.NumberOfColumns # Размер таблицы
    # Алгоритм перебора
    def foo():
        _ret = ''
        for column in range(columns):
            _ret += ''.join([selected_size_table.AsValueString(row, column).ToString(), ';'])
        _ret = _ret[:-1]
        return _ret

    returned_string = ''
    for row in range(rows):
        returned_string += ''.join([foo(),'\n'])
    returned_string = returned_string[:-1]
    
    # Получение шапки таблица:
    print(selected_size_table.GetColumnHeader(1).Name)

    # Запись:
    # path = ''.join([forms.select_folder(), '\\', selected_size_table_name, '.csv'])
    # sw = System.IO.StreamWriter(path)
    # sw.Write(returned_string)
    # sw.Close()

else:
    forms.Alert('Это документ', exit=True)
