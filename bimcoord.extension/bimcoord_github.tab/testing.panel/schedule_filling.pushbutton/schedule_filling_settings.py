# -*- coding: utf-8 -*-
from Autodesk.Revit import DB
import System

class Category:

    def __init__(self, document, category_name, category_ost):
        self.document = document
        self.category_ost = category_ost

