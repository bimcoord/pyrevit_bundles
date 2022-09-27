# -*- coding: utf-8 -*-
__title__ = '''Запустить
скрипт'''
__doc__ = '''Временный бандл для быстрого создания и запуска скрипта'''

from Autodesk.Revit import DB

uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document

from schedule_filling_settings import Category

pipe_category = Category(doc, "Трубы", DB.BuiltInCategory.OST_PipeCurves)

print(pipe_category.elements)

# pipe_category.fill_parameter(lambda : 1)

