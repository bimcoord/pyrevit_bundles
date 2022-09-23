# -*- coding: utf-8 -*-
__title__ = 'Export\nCSV'
__doc__ = '''Define later in bundle.yaml'''
# Template
from Autodesk.Revit import DB
from rpw.ui import forms

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
    selected_size_table = family_size_table_manager.GetSizeTable(selected_size_table)

    #Алгоритм перебора
    # Размер таблицы:
    columns = selected_size_table.NumberOfColumns
    rows = selected_size_table.NumberOfRows

    # Получение шапки таблица. Также под вопросом 
    # print(columns,rows)
    # print(selected_size_table.GetColumnHeader(2).GetUnitTypeId()) # Получение информации о типе под вопросом

else:
    forms.Alert('Это документ', exit=True)
