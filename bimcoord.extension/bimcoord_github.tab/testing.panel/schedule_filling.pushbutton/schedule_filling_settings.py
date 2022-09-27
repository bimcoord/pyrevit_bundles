# -*- coding: utf-8 -*-
from Autodesk.Revit import DB
import System

class Category:

    def __init__(self, document, category_name, category_ost):
        self.document = document
        self.category_ost = category_ost
        self.category_name = category_name

        self.elements = Category._get_elements(self)

    def _get_elements(self): # Исключить элементы
        elements = DB.FilteredElementCollector(self.document).\
            OfCategory(self.category_ost).\
            WhereElementIsNotElementType().\
            ToElements()
        return elements

    # def fill_parameter(self, parameter_guid,func_to_calc_param):
    #     parameter_guid = System.Guid(parameter_guid)
    #     parameter_type = parameter_guid.GetDefinition().
    #     transaction = DB.Transaction(self.document, "Заполнение параметров")
    #     transaction.Start()
    #     for element in self.elements:
    #         value = func_to_calc_param()
    #         element.get_Parameter(parameter_guid).Set(value) # Тип заполняемого параметра
    #     transaction.Commit()

