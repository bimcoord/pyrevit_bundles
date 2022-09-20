# -*- coding: utf-8 -*-
__title__ = 'Export\nCSV'
__doc__ = '''Define later in bundle.yaml'''
# Template
from Autodesk.Revit import DB
from rpw.ui import forms

doc = __revit__.ActiveUIDocument.Document



# Checking document like family or project
if doc.IsFamilyDocument:
    forms.Alert('Это семейство', exit=True)
else:
    forms.Alert('Это документ', exit=True)
